from __future__ import annotations
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import date, time, timedelta

from core_api.core.db import get_session
from core_api.core.security import hash_password
from core_api.models import User, Employee, Week, Shift, Availability
from core_api.core.logging import logger
from core_api.core.constants import DEMO_USER_ID, DEMO_EMAIL, DEMO_PASSWORD

router = APIRouter(prefix="/dev", tags=["dev"])


def next_monday(d: date) -> date:
    return d + timedelta(days=(7 - d.weekday()))


@router.post("/seed", status_code=status.HTTP_200_OK)
def seed(db: Session = Depends(get_session)):
    """
    Populate (or ensure) consistent demo data for the demo user.
    - 5 active employees
    - Week starting next Monday, open_days = Mon..Sat
    - Shifts 09:00-13:00 and 13:00-18:00 (min_staff=2 Mon-Fri, 3 Sat)
    - Availabilities Mon-Fri 09:00-18:00 for all employees
    """

    logger.info(f"Seeding started")

    # 0) Clear demo user
    db.query(User).filter(User.id == DEMO_USER_ID).delete(synchronize_session=False)
    logger.info("Demo user cleared")

    # 1) USER
    user = User(
        id=DEMO_USER_ID, email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD)
    )
    db.add(user)
    db.flush()
    logger.info("Demo user created")

    # 2) EMPLOYEES
    names: list[str] = ["Artur", "Arthur", "Angelo", "Gabriel", "Guilherme"]
    for n in names:
        db.add(Employee(user_id=user.id, name=n, active=True))
    db.flush()
    logger.info("Seed employees created")

    # 3) WEEK (next Monday; your schemas use open_days: List[int])
    start = next_monday(date.today())
    # Mon..Sat => [0,1,2,3,4,5]  (0=Mon ... 6=Sun),
    week = Week(
        user_id=user.id,
        start_date=start,
        open_days=[0, 1, 2, 3, 4, 5],
        approved=False,
    )
    db.add(week)
    db.flush()
    logger.info("Seed week created")

    # 4) SHIFTS
    for wd in week.open_days:  # according to your Week.open_days (int[] 0..6)
        # ensure local_date is consistent with the week
        local_date = start + timedelta(days=wd)
        min_staff = 2 if wd < 5 else 3  # Mon–Fri=2, Sat=3
        db.add_all(
            [
                Shift(
                    user_id=user.id,
                    week_id=week.id,
                    weekday=wd,
                    local_date=local_date,
                    start_time=time(9, 0),
                    end_time=time(13, 0),
                    min_staff=min_staff,
                ),
                Shift(
                    user_id=user.id,
                    week_id=week.id,
                    weekday=wd,
                    local_date=local_date,
                    start_time=time(13, 0),
                    end_time=time(18, 0),
                    min_staff=min_staff,
                ),
            ]
        )
    logger.info("Seed shifts created")

    # 5) AVAILABILITIES (Mon–Fri 09–18 for all active employees)
    employees = db.query(Employee).filter_by(user_id=user.id, active=True).all()
    for emp in employees:
        for wd in [0, 1, 2, 3, 4]:  # Mon..Fri
            db.add(
                Availability(
                    user_id=user.id,
                    employee_id=emp.id,
                    weekday=wd,
                    start_time=time(9, 0),
                    end_time=time(18, 0),
                )
            )
    logger.info("Seed availabilities created")

    return {
        "user_id": str(user.id),
        "week_id": str(week.id),
        "week_start": str(week.start_date),
        "open_days": week.open_days,
        "employees": len(employees),
    }
