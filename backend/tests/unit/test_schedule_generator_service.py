import uuid

import pytest
from fastapi.testclient import TestClient

import app.schemas.schedule as schemas
from schedule_generator.main import app
from schedule_generator.domain.solver import ScheduleGenerator
from schedule_generator.services import generator as generator_service


def _build_dispatch_request():
    employee_morning_id = uuid.uuid4()
    employee_afternoon_id = uuid.uuid4()

    payload = schemas.ScheduleGenerationDispatchPayload(
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
    return schemas.ScheduleGenerationDispatchRequest(
        job_id=uuid.uuid4(),
        callback_url="http://main-api/api/v1/internal/schedule-generation-results",
        payload=payload,
    )


@pytest.mark.unit
def test_schedule_generator_from_payload_builds_expected_assignments():
    dispatch_request = _build_dispatch_request()

    generator = ScheduleGenerator.from_payload(payload=dispatch_request.payload)

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
def test_build_schedule_preview_returns_preview_for_feasible_payload():
    dispatch_request = _build_dispatch_request()

    preview = generator_service.build_schedule_preview(dispatch_request)

    assert preview.possible is True
    assert len(preview.schedule.shifts) == 2
    assert preview.schedule.shifts[0].employees[0].name == "Morning Employee"
    assert preview.schedule.shifts[1].employees[0].name == "Afternoon Employee"


@pytest.mark.unit
def test_generate_schedule_route_accepts_job_and_sends_callback(monkeypatch):
    client = TestClient(app)
    dispatch_request = _build_dispatch_request()
    sent_callbacks = []

    def fake_send_schedule_generation_callback(*, dispatch_request, callback_payload):
        sent_callbacks.append((dispatch_request, callback_payload))

    monkeypatch.setattr(
        generator_service,
        "send_schedule_generation_callback",
        fake_send_schedule_generation_callback,
    )

    response = client.post(
        "/internal/generate-schedule",
        json=dispatch_request.model_dump(mode="json"),
    )

    assert response.status_code == 202
    assert response.json() == {
        "job_id": str(dispatch_request.job_id),
        "status": "processing",
    }
    assert len(sent_callbacks) == 1
    sent_request, callback_payload = sent_callbacks[0]
    assert sent_request.job_id == dispatch_request.job_id
    assert callback_payload.status == schemas.ScheduleGenerationJobStatus.DONE
    assert callback_payload.result.possible is True


@pytest.mark.unit
def test_process_schedule_generation_job_reports_failure_when_preview_breaks(monkeypatch):
    dispatch_request = _build_dispatch_request()
    sent_callbacks = []

    def failing_build_schedule_preview(_dispatch_request):
        raise RuntimeError("boom")

    def fake_send_schedule_generation_callback(*, dispatch_request, callback_payload):
        sent_callbacks.append((dispatch_request, callback_payload))

    monkeypatch.setattr(
        generator_service,
        "build_schedule_preview",
        failing_build_schedule_preview,
    )
    monkeypatch.setattr(
        generator_service,
        "send_schedule_generation_callback",
        fake_send_schedule_generation_callback,
    )

    generator_service.process_schedule_generation_job(dispatch_request)

    assert len(sent_callbacks) == 1
    sent_request, callback_payload = sent_callbacks[0]
    assert sent_request.job_id == dispatch_request.job_id
    assert callback_payload.status == schemas.ScheduleGenerationJobStatus.FAILED
    assert callback_payload.result is None
    assert callback_payload.error == "schedule generation failed"
