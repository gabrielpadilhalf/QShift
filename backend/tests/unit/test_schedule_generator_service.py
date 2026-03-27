import uuid

import pytest
from fastapi.testclient import TestClient

import app.schemas.schedule as schemas
from app.services.schedule import ScheduleGenerator
from schedule_generator.main import app


def _build_dispatch_payload():
    employee_morning_id = uuid.uuid4()
    employee_afternoon_id = uuid.uuid4()

    return schemas.ScheduleGenerationDispatchPayload(
        shift_vector=[
            schemas.PreviewShiftBase(
                id=uuid.uuid4(),
                weekday=0,
                start_time="09:00",
                end_time="12:00",
                min_staff=1,
            ),
            schemas.PreviewShiftBase(
                id=uuid.uuid4(),
                weekday=0,
                start_time="13:00",
                end_time="17:00",
                min_staff=1,
            ),
        ],
        employees=[
            schemas.ScheduleGenerationEmployeeOut(
                id=employee_morning_id,
                name="Morning Employee",
            ),
            schemas.ScheduleGenerationEmployeeOut(
                id=employee_afternoon_id,
                name="Afternoon Employee",
            ),
        ],
        availabilities=[
            schemas.ScheduleGenerationAvailabilityOut(
                employee_id=employee_morning_id,
                weekday=0,
                start_time="09:00",
                end_time="12:00",
            ),
            schemas.ScheduleGenerationAvailabilityOut(
                employee_id=employee_afternoon_id,
                weekday=0,
                start_time="13:00",
                end_time="17:00",
            ),
        ],
    )


@pytest.mark.unit
def test_schedule_generator_from_payload_builds_expected_assignments():
    payload = _build_dispatch_payload()

    generator = ScheduleGenerator.from_payload(payload=payload)

    assert generator.check_possibility() is True

    schedule = generator.generate_schedule()
    assert len(schedule.shifts) == 2

    morning_shift = schedule.shifts[0]
    afternoon_shift = schedule.shifts[1]

    assert [employee.name for employee in morning_shift.employees] == [
        "Morning Employee"
    ]
    assert [employee.name for employee in afternoon_shift.employees] == [
        "Afternoon Employee"
    ]


@pytest.mark.unit
def test_schedule_generator_service_returns_preview_for_feasible_payload():
    client = TestClient(app)
    payload = _build_dispatch_payload()

    response = client.post(
        "/internal/generate-schedule",
        json={
            "job_id": str(uuid.uuid4()),
            "payload": payload.model_dump(mode="json"),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["possible"] is True
    assert len(data["schedule"]["shifts"]) == 2
    assert data["schedule"]["shifts"][0]["employees"][0]["name"] == "Morning Employee"
    assert data["schedule"]["shifts"][1]["employees"][0]["name"] == "Afternoon Employee"


@pytest.mark.unit
def test_schedule_generator_service_returns_not_possible_without_employees():
    client = TestClient(app)
    payload = _build_dispatch_payload()

    response = client.post(
        "/internal/generate-schedule",
        json={
            "job_id": str(uuid.uuid4()),
            "payload": {
                **payload.model_dump(mode="json"),
                "employees": [],
                "availabilities": [],
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {"possible": False, "schedule": None}


@pytest.mark.unit
def test_schedule_generator_service_returns_not_possible_without_availabilities():
    client = TestClient(app)
    payload = _build_dispatch_payload()

    response = client.post(
        "/internal/generate-schedule",
        json={
            "job_id": str(uuid.uuid4()),
            "payload": {
                **payload.model_dump(mode="json"),
                "availabilities": [],
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {"possible": False, "schedule": None}
