from uuid import UUID
from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session

from core_api.core.db import get_session
from core_api.api.dependencies import current_user_id
from core_api.schemas.availability import (
    AvailabilityCreate,
    AvailabilityOut,
    AvailabilityUpdate,
)
from core_api.models.availability import Availability
from core_api.models.employee import Employee

router = APIRouter(
    prefix="/employees/{employee_id}/availabilities", tags=["availabilities"]
)


# HELPERS
def _get_employee(employee_id: UUID, user_id: UUID, db: Session):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id, Employee.user_id == user_id)
        .first()
    )
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )
    return employee


def _get_availability(
    availability_id: UUID, employee_id: UUID, user_id: UUID, db: Session
):
    availability = (
        db.query(Availability)
        .filter(
            Availability.user_id == user_id,
            Availability.employee_id == employee_id,
            Availability.id == availability_id,
        )
        .first()
    )
    if availability is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found"
        )
    return availability


# CREATE
@router.post("", response_model=AvailabilityOut, status_code=status.HTTP_201_CREATED)
def create_availability(
    payload: AvailabilityCreate,
    response: Response,
    employee_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    _get_employee(employee_id, user_id, db)

    availability = Availability(
        user_id=user_id, employee_id=employee_id, **payload.model_dump()
    )

    db.add(availability)
    db.flush()
    db.refresh(availability)

    response.headers["Location"] = (
        f"/employees/{employee_id}/availabilities/{availability.id}"
    )

    return availability


# READ
@router.get("", response_model=list[AvailabilityOut], status_code=status.HTTP_200_OK)
def read_availabilities(
    employee_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    _get_employee(employee_id, user_id, db)

    availabilities = (
        db.query(Availability)
        .filter(
            Availability.employee_id == employee_id, Availability.user_id == user_id
        )
        .order_by(Availability.weekday, Availability.start_time)
        .all()
    )

    return availabilities


# UPDATE
@router.patch(
    "/{availability_id}", response_model=AvailabilityOut, status_code=status.HTTP_200_OK
)
def update_availability(
    payload: AvailabilityUpdate,
    employee_id: UUID,
    availability_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    _get_employee(employee_id, user_id, db)
    availability = _get_availability(availability_id, employee_id, user_id, db)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(availability, field, value)

    db.flush()
    db.refresh(availability)

    return availability


# DELETE
@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(
    employee_id: UUID,
    availability_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    _get_employee(employee_id, user_id, db)
    availability = _get_availability(availability_id, employee_id, user_id, db)

    db.delete(availability)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
