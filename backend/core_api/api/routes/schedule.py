from uuid import UUID
from fastapi import APIRouter, Request, status, Depends, HTTPException
from sqlalchemy.orm import Session

import core_api.schemas.schedule as schemas
import core_api.services.schedule as schedule_service
from core_api.models import ShiftAssignment, Employee, ScheduleGenerationJob, Week
from core_api.models.shift import Shift
from core_api.api.dependencies import current_user_id
from core_api.core.config import settings
from core_api.core.db import get_session

router = APIRouter(prefix="", tags=["schedule"])

# CREATE
@router.post(
    "/weeks/{week_id}/schedule", response_model=schemas.ScheduleOut, status_code=status.HTTP_201_CREATED
)
def create_schedule(
    week_id: UUID,
    payload: schemas.ScheduleCreate,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    for schedule_shift in payload.shifts:
        if db.get(Shift, schedule_shift.shift_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found"
            )
        for employee_id in schedule_shift.employee_ids:
            if db.get(Employee, employee_id) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
                )
            new_assignment = ShiftAssignment(
                user_id=user_id,
                shift_id=schedule_shift.shift_id,
                employee_id=employee_id,
            )
            db.add(new_assignment)

    db.commit()

    return schedule_service.build_schedule_schema_from_db(week_id, user_id, db)


# READ
@router.get("/weeks/{week_id}/schedule", response_model=schemas.ScheduleOut, status_code=status.HTTP_200_OK)
def read_schedule(
    week_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    return schedule_service.build_schedule_schema_from_db(week_id, user_id, db)


# DELETE
@router.delete("/weeks/{week_id}/schedule", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    week_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    week = db.query(Week).filter(Week.user_id == user_id, Week.id == week_id).first()

    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Week not found"
        )

    shift_ids_tuple = db.query(Shift.id).filter(Shift.week_id == week_id).all()
    shift_ids = []
    for shift_id_tuple in shift_ids_tuple:
        shift_ids.append(shift_id_tuple[0])

    db.query(ShiftAssignment).filter(ShiftAssignment.shift_id.in_(shift_ids)).delete(
        synchronize_session=False
    )

    db.commit()


# GENERATE PREVIEW SCHEDULE
@router.post(
    "/preview-schedule",
    response_model=schemas.ScheduleGenerationJobAcceptedOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_preview_schedule(
    payload: schemas.ShiftVectorIn,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    dispatch_payload = schedule_service.build_schedule_generation_payload(
        db=db,
        user_id=user_id,
        shift_vector=payload.shift_vector,
    )
    job = ScheduleGenerationJob(
        user_id=user_id,
        status=schemas.ScheduleGenerationJobStatus.PENDING.value,
        request_payload={},
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    dispatch_request = schedule_service.build_schedule_generation_dispatch_request(
        job_id=job.id,
        payload=dispatch_payload,
    )
    job.request_payload = dispatch_request.model_dump(mode="json")

    try:
        schedule_service.dispatch_schedule_generation_job(dispatch_request)
    except RuntimeError as exc:
        job.status = schemas.ScheduleGenerationJobStatus.FAILED.value
        job.error_message = str(exc)
        job.finished_at = schedule_service.utcnow()
    else:
        job.status = schemas.ScheduleGenerationJobStatus.PROCESSING.value
        job.error_message = None

    db.add(job)
    db.commit()

    return schemas.ScheduleGenerationJobAcceptedOut(
        job_id=job.id,
        status=schemas.ScheduleGenerationJobStatus(job.status),
    )


@router.post(
    "/internal/schedule-generation-results",
    response_model=schemas.ScheduleGenerationJobOut,
    status_code=status.HTTP_200_OK,
)
async def receive_schedule_generation_result(
    request: Request,
    db: Session = Depends(get_session),
):
    raw_body = await request.body()
    timestamp = request.headers.get("X-Timestamp")
    signature = request.headers.get("X-Signature")

    if timestamp is None or signature is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing callback authentication headers",
        )

    if not schedule_service.is_schedule_callback_timestamp_valid(
        timestamp=timestamp,
        tolerance_seconds=settings.SCHEDULE_CALLBACK_TOLERANCE_SECONDS,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid callback timestamp",
        )

    if not schedule_service.is_schedule_callback_signature_valid(
        secret=settings.SCHEDULE_CALLBACK_SECRET,
        timestamp=timestamp,
        raw_body=raw_body,
        provided_signature=signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid callback signature",
        )

    callback_payload = schemas.ScheduleGenerationCallbackIn.model_validate_json(raw_body)
    job = db.get(ScheduleGenerationJob, callback_payload.job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule generation job not found",
        )

    try:
        job_schema = schedule_service.apply_schedule_generation_callback(
            job=job,
            callback_payload=callback_payload,
        )
    except ValueError as exc:
        if str(exc) == "schedule generation job already finalized":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    db.add(job)
    db.commit()
    return job_schema


@router.get(
    "/schedule-generation-jobs/{job_id}",
    response_model=schemas.ScheduleGenerationJobOut,
    status_code=status.HTTP_200_OK,
)
def read_schedule_generation_job(
    job_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    job = (
        db.query(ScheduleGenerationJob)
        .filter(
            ScheduleGenerationJob.id == job_id,
            ScheduleGenerationJob.user_id == user_id,
        )
        .first()
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule generation job not found",
        )

    return schedule_service.build_schedule_generation_job_schema(job)
