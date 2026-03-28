from uuid import UUID
from datetime import timedelta
from fastapi import APIRouter, status, Response, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core_api.schemas.shift import ShiftCreate, ShiftOut, ShiftUpdate
from core_api.models.shift import Shift
from core_api.models.week import Week
from core_api.api.dependencies import current_user_id
from core_api.core.db import get_session


router = APIRouter(prefix="/weeks/{week_id}/shifts", tags=["shifts"])


# HELPERS
def _get_shift(user_id: UUID, week_id: UUID, shift_id: UUID, db: Session) -> Shift:
    shift = (
        db.query(Shift)
        .filter(
            Shift.user_id == user_id, Shift.week_id == week_id, Shift.id == shift_id
        )
        .first()
    )

    if shift is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found"
        )

    return shift


def _get_week(user_id: UUID, week_id: UUID, db: Session) -> Week:
    week = db.query(Week).filter(Week.user_id == user_id, Week.id == week_id).first()

    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Week not found"
        )

    return week


# CREATE
@router.post("", response_model=ShiftOut, status_code=status.HTTP_201_CREATED)
def create_shift(
    week_id: UUID,
    payload: ShiftCreate,
    response: Response,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    week = _get_week(user_id, week_id, db)

    data = payload.model_dump()
    data["local_date"] = week.start_date + timedelta(days=data["weekday"])

    shift = Shift(week_id=week_id, user_id=user_id, **data)

    db.add(shift)
    db.flush()
    db.refresh(shift)

    response.headers["Location"] = f"/weeks/{week_id}/shifts/{shift.id}"

    return shift


# READ
@router.get("", response_model=list[ShiftOut], status_code=status.HTTP_200_OK)
def list_shifts(
    week_id: UUID,
    weekday: int | None = Query(
        default=None,
        ge=0,
        le=6,
        description="Optional filter: weekday 0=Mon ... 6=Sun",
    ),
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    _get_week(user_id, week_id, db)

    query = db.query(Shift).filter(Shift.user_id == user_id, Shift.week_id == week_id)

    if weekday is not None:
        query = query.filter(Shift.weekday == weekday)

    shifts = query.order_by(Shift.weekday, Shift.start_time).all()

    return shifts


@router.get("/{shift_id}", response_model=ShiftOut, status_code=status.HTTP_200_OK)
def read_shift(
    week_id: UUID,
    shift_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    return _get_shift(user_id, week_id, shift_id, db)


# UPDATE
@router.patch("/{shift_id}", response_model=ShiftOut, status_code=status.HTTP_200_OK)
def update_shift(
    week_id: UUID,
    shift_id: UUID,
    payload: ShiftUpdate,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    week = _get_week(user_id, week_id, db)
    shift = _get_shift(user_id, week_id, shift_id, db)

    data = payload.model_dump(exclude_unset=True)

    if not data:
        return shift

    if "weekday" in data:
        data["local_date"] = week.start_date + timedelta(days=data["weekday"])

    for field, value in data.items():
        setattr(shift, field, value)

    db.flush()
    db.refresh(shift)

    return shift


# DELETE
@router.delete("/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift(
    week_id: UUID,
    shift_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    _get_week(user_id, week_id, db)

    shift = _get_shift(user_id, week_id, shift_id, db)

    db.delete(shift)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
