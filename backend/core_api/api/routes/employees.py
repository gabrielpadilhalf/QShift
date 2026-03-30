from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from core_api.core.db import get_session
from core_api.api.dependencies import current_user_id
from core_api.models.employee import Employee
import core_api.services.employee as employee_service
import core_api.services.schedule as schedule_service
from core_api.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeOut,
    EmployeeMonthReport,
    EmployeeYearReport,
)

router = APIRouter(prefix="/employees", tags=["employees"])


# HELPERS
def _get_employee(employee_id: UUID, user_id: UUID, db: Session):
    employee = (
        db.query(Employee)
        .filter(Employee.user_id == user_id, Employee.id == employee_id)
        .first()
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    return employee


# CREATE
@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    response: Response,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    employee = Employee(user_id=user_id, **payload.model_dump())

    db.add(employee)
    db.flush()
    db.refresh(employee)

    response.headers["Location"] = f"/employees/{employee.id}"

    return employee


# READ
@router.get("", response_model=list[EmployeeOut], status_code=status.HTTP_200_OK)
def list_employees(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(current_user_id),
):
    background_tasks.add_task(schedule_service.wake_schedule_generator)

    employees = (
        db.query(Employee)
        .filter(Employee.user_id == user_id)
        .order_by(Employee.name)
        .all()
    )

    return employees


@router.get(
    "/{employee_id}", response_model=EmployeeOut, status_code=status.HTTP_200_OK
)
def read_employee(
    employee_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    return _get_employee(employee_id, user_id, db)


# UPDATE
@router.patch(
    "/{employee_id}", response_model=EmployeeOut, status_code=status.HTTP_200_OK
)
def update_employee(
    payload: EmployeeUpdate,
    employee_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    employee = _get_employee(employee_id, user_id, db)

    data = payload.model_dump(exclude_unset=True)
    if not data:
        return employee

    for field, value in data.items():
        setattr(employee, field, value)

    db.flush()
    db.refresh(employee)

    return employee


# DELETE
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: UUID,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    employee = _get_employee(employee_id, user_id, db)

    db.delete(employee)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# GET MONTH REPORT
@router.get(
    "/{employee_id}/report/{year}/{month}",
    response_model=EmployeeMonthReport,
    status_code=status.HTTP_200_OK,
)
def get_employee_month_report(
    employee_id: UUID,
    year: int,
    month: int,
    db: Session = Depends(get_session),
):
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12",
        )

    if year <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be a positive integer",
        )

    employee_name = (
        db.execute(select(Employee.name).where(Employee.id == employee_id))
        .scalars()
        .first()
    )

    if employee_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    return employee_service.build_employee_month_report(
        employee_id, employee_name, year, month, db
    )


@router.get(
    "/{employee_id}/report/{year}",
    response_model=EmployeeYearReport,
    status_code=status.HTTP_200_OK,
)
def get_employee_year_report(
    employee_id: UUID,
    year: int,
    db: Session = Depends(get_session),
):
    if year <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be a positive integer",
        )

    employee_name = (
        db.execute(select(Employee.name).where(Employee.id == employee_id))
        .scalars()
        .first()
    )

    if employee_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    return employee_service.build_employee_year_report(
        employee_id, employee_name, year, db
    )
