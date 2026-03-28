from fastapi import APIRouter, BackgroundTasks, status

import app.schemas.schedule as schemas
from schedule_generator.services.generator import process_schedule_generation_job

router = APIRouter()


@router.post(
    "/internal/generate-schedule",
    response_model=schemas.ScheduleGenerationJobAcceptedOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_schedule(
    dispatch_request: schemas.ScheduleGenerationDispatchRequest,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        process_schedule_generation_job,
        dispatch_request,
    )
    return schemas.ScheduleGenerationJobAcceptedOut(
        job_id=dispatch_request.job_id,
        status=schemas.ScheduleGenerationJobStatus.PROCESSING,
    )
