from uuid import UUID
from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session

from core_api.schemas.week import WeekCreate, WeekOut, WeekUpdate
from core_api.api.dependencies import current_user_id
from core_api.core.db import get_session
from core_api.models.week import Week


router = APIRouter(prefix="/weeks", tags=["weeks"])


# HELPERS
def _get_week(week_id: UUID, user_id: UUID, db: Session):
    week = db.query(Week).filter(Week.id == week_id, Week.user_id == user_id).first()

    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Week not found"
        )

    return week


# CREATE
@router.post("", response_model=WeekOut, status_code=status.HTTP_201_CREATED)
def create_week(
    payload: WeekCreate,
    response: Response,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    week = Week(**payload.model_dump(), user_id=user_id)

    db.add(week)
    db.flush()
    db.refresh(week)

    response.headers["Location"] = f"/weeks/{week.id}"

    return week


# READ
@router.get("", response_model=list[WeekOut], status_code=status.HTTP_200_OK)
def list_weeks(
    user_id: UUID = Depends(current_user_id), db: Session = Depends(get_session)
):
    return (
        db.query(Week)
        .filter(Week.user_id == user_id)
        .order_by(Week.start_date.desc())
        .all()
    )


@router.get("/{week_id}", response_model=WeekOut, status_code=status.HTTP_200_OK)
def read_week(
    week_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    return _get_week(week_id, user_id, db)


# UPDATE
@router.patch("/{week_id}", response_model=WeekOut, status_code=status.HTTP_200_OK)
def update_week(
    week_id: UUID,
    payload: WeekUpdate,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    week = _get_week(week_id, user_id, db)

    data = payload.model_dump(exclude_unset=True)
    if not data:
        return week

    for field, value in data.items():
        setattr(week, field, value)

    db.flush()
    db.refresh(week)

    return week


# DELETE
@router.delete("/{week_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_week(
    week_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    week = _get_week(week_id, user_id, db)

    db.delete(week)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
