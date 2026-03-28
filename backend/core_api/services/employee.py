from uuid import UUID
from datetime import datetime, date, time, timedelta
import calendar

from sqlalchemy import select
from sqlalchemy.orm import Session

from core_api.models import ShiftAssignment, Shift
from core_api.schemas.employee import (
    EmployeeMonthReport,
    EmployeeYearReport,
    EmployeeMonthData,
)

# HELPERS


def _time_diff(start_time: time, end_time: time) -> timedelta:
    datetime1 = datetime.combine(datetime.today(), start_time)
    datetime2 = datetime.combine(datetime.today(), end_time)
    return datetime2 - datetime1


def _build_employee_month_data(
    employee_id: UUID, year: int, month: int, db: Session
) -> EmployeeMonthData:
    shift_ids = (
        db.execute(
            select(ShiftAssignment.shift_id).where(
                ShiftAssignment.employee_id == employee_id
            )
        )
        .scalars()
        .all()
    )

    start_date = date(year, month, 1)
    last_month_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_month_day)

    shifts = (
        db.execute(
            select(Shift)
            .where(
                Shift.id.in_(shift_ids),
                Shift.local_date >= start_date,
                Shift.local_date <= end_date,
            )
            .order_by(Shift.local_date)
        )
        .scalars()
        .all()
    )

    if not shifts:
        return EmployeeMonthData(
            hours_worked=0.0,
            num_days_off=(end_date - start_date).days + 1,
            num_days_worked=0,
            num_morning_shifts=0,
            num_afternoon_shifts=0,
            num_night_shifts=0,
        )

    hours_worked = 0.0
    num_days_worked = 0
    num_morning_shifts = 0
    num_afternoon_shifts = 0
    num_night_shifts = 0

    last_date = None
    for shift in shifts:
        hours_worked += (
            _time_diff(shift.start_time, shift.end_time).total_seconds() / 3600.0
        )
        if last_date is None or last_date != shift.local_date:
            num_days_worked += 1

        if shift.start_time < time(12):
            num_morning_shifts += 1
        elif shift.start_time < time(18):
            num_afternoon_shifts += 1
        else:
            num_night_shifts += 1

        last_date = shift.local_date

    num_days_off = (end_date - start_date).days + 1 - num_days_worked

    return EmployeeMonthData(
        hours_worked=hours_worked,
        num_days_off=num_days_off,
        num_days_worked=num_days_worked,
        num_morning_shifts=num_morning_shifts,
        num_afternoon_shifts=num_afternoon_shifts,
        num_night_shifts=num_night_shifts,
    )


# SERVICES


def build_employee_month_report(
    employee_id: UUID, employee_name: str, year: int, month: int, db: Session
) -> EmployeeMonthReport:
    return EmployeeMonthReport(
        name=employee_name,
        month_data=_build_employee_month_data(employee_id, year, month, db),
    )


def build_employee_year_report(
    employee_id: UUID, employee_name: str, year: int, db: Session
) -> EmployeeYearReport:
    months_data = []
    for month in range(1, 13):
        months_data.append(_build_employee_month_data(employee_id, year, month, db))

    return EmployeeYearReport(name=employee_name, months_data=months_data)
