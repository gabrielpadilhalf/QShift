import json
import time

import pytest
from fastapi.testclient import TestClient

import core_api.services.schedule as schedule_service
from core_api.core.config import settings


def _normalize_preview_shift_vector(shifts):
    return [
        {
            "id": shift["id"],
            "weekday": shift["weekday"],
            "start_time": shift["start_time"],
            "end_time": shift["end_time"],
            "min_staff": shift["min_staff"],
        }
        for shift in shifts
    ]


def _build_signed_callback_headers(raw_body: bytes, timestamp: str | None = None):
    if timestamp is None:
        timestamp = str(int(time.time()))
    signature = schedule_service.build_schedule_callback_signature(
        secret=settings.SCHEDULE_CALLBACK_SECRET,
        timestamp=timestamp,
        raw_body=raw_body,
    )
    return {
        "Content-Type": "application/json",
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }


@pytest.mark.integration
def test_create_schedule_success(client: TestClient, seeded_data):
    """Should create schedule with valid assignments."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    shift_id = shifts[0]["id"]
    employee_id = employees[0]["id"]

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={
            "shifts": [
                {"shift_id": shift_id, "employee_ids": [employee_id]},
            ]
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "shifts" in data
    assert len(data["shifts"]) > 0


@pytest.mark.integration
def test_create_schedule_multiple_employees(client: TestClient, seeded_data):
    """Should create schedule with multiple employees per shift."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    shift_id = shifts[0]["id"]
    employee_ids = [employees[0]["id"], employees[1]["id"]]

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={
            "shifts": [
                {"shift_id": shift_id, "employee_ids": employee_ids},
            ]
        },
    )

    assert response.status_code == 201
    data = response.json()
    shift_data = next(s for s in data["shifts"] if s["shift_id"] == shift_id)
    assert len(shift_data["employees"]) == 2


@pytest.mark.integration
def test_create_schedule_shift_not_found(client: TestClient, seeded_data):
    """Should return 404 when creating schedule with non-existent shift."""
    week_id = seeded_data["week_id"]
    employees = client.get("/api/v1/employees").json()
    fake_shift_id = "00000000-0000-0000-0000-000000000999"

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={
            "shifts": [
                {"shift_id": fake_shift_id, "employee_ids": [employees[0]["id"]]},
            ]
        },
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_create_schedule_employee_not_found(client: TestClient, seeded_data):
    """Should return 404 when creating schedule with non-existent employee."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    fake_employee_id = "00000000-0000-0000-0000-000000000999"

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={
            "shifts": [
                {"shift_id": shifts[0]["id"], "employee_ids": [fake_employee_id]},
            ]
        },
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_read_schedule_success(client: TestClient, seeded_data):
    """Should return existing schedule."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={
            "shifts": [
                {"shift_id": shifts[0]["id"], "employee_ids": [employees[0]["id"]]},
            ]
        },
    )

    response = client.get(f"/api/v1/weeks/{week_id}/schedule")

    assert response.status_code == 200
    data = response.json()
    assert "shifts" in data
    assert len(data["shifts"]) > 0


@pytest.mark.integration
def test_read_schedule_empty(client: TestClient, seeded_data):
    """Should return empty schedule when no assignments exist."""
    week_id = seeded_data["week_id"]
    response = client.get(f"/api/v1/weeks/{week_id}/schedule")

    assert response.status_code == 200
    data = response.json()
    assert "shifts" in data
    for shift in data["shifts"]:
        assert shift["employees"] == []


@pytest.mark.integration
def test_read_schedule_structure(client: TestClient, seeded_data):
    """Should return schedule with correct structure."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={
            "shifts": [
                {"shift_id": shifts[0]["id"], "employee_ids": [employees[0]["id"]]},
            ]
        },
    )

    response = client.get(f"/api/v1/weeks/{week_id}/schedule")

    assert response.status_code == 200
    data = response.json()
    assert "shifts" in data

    for shift in data["shifts"]:
        assert "shift_id" in shift
        assert "weekday" in shift
        assert "start_time" in shift
        assert "end_time" in shift
        assert "min_staff" in shift
        assert "employees" in shift

        for employee in shift["employees"]:
            assert "employee_id" in employee
            assert "name" in employee


@pytest.mark.integration
def test_preview_schedule_creates_processing_job_and_dispatches_payload(
    client: TestClient,
    seeded_data,
    dispatched_schedule_jobs,
):
    """Should create a processing job and dispatch the complete generation payload."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    response = client.post("/api/v1/preview-schedule", json={"shift_vector": shifts})

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"
    assert len(dispatched_schedule_jobs) == 1

    dispatch_request = dispatched_schedule_jobs[0]
    assert str(dispatch_request.job_id) == data["job_id"]
    assert (
        dispatch_request.payload.model_dump(mode="json")["shift_vector"]
        == _normalize_preview_shift_vector(shifts)
    )
    assert dispatch_request.callback_url.endswith(
        "/api/v1/internal/schedule-generation-results"
    )
    assert len(dispatch_request.payload.employees) == len(employees)
    assert len(dispatch_request.payload.availabilities) > 0

    job_response = client.get(f"/api/v1/schedule-generation-jobs/{data['job_id']}")
    assert job_response.status_code == 200
    assert job_response.json() == {
        "job_id": data["job_id"],
        "status": "processing",
        "result": None,
        "error": None,
    }


@pytest.mark.integration
def test_preview_schedule_does_not_persist_assignments(
    client: TestClient,
    seeded_data,
    dispatched_schedule_jobs,
):
    """Should create only a preview job and keep persisted schedule empty."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts},
    )
    assert preview_response.status_code == 202
    assert len(dispatched_schedule_jobs) == 1

    schedule_response = client.get(f"/api/v1/weeks/{week_id}/schedule")
    assert schedule_response.status_code == 200
    schedule_data = schedule_response.json()

    for shift in schedule_data["shifts"]:
        assert shift["employees"] == []


@pytest.mark.integration
def test_preview_schedule_dispatches_empty_employee_list_when_none_exist(
    client: TestClient,
    dispatched_schedule_jobs,
):
    """Should dispatch a job with no employees when the user has none."""
    client.post("/api/v1/dev/seed")
    employees = client.get("/api/v1/employees").json()
    for employee in employees:
        client.delete(f"/api/v1/employees/{employee['id']}")

    weeks = client.get("/api/v1/weeks").json()
    week_id = weeks[0]["id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    response = client.post("/api/v1/preview-schedule", json={"shift_vector": shifts})

    assert response.status_code == 202
    assert response.json()["status"] == "processing"
    assert len(dispatched_schedule_jobs[0].payload.employees) == 0
    assert len(dispatched_schedule_jobs[0].payload.availabilities) == 0


@pytest.mark.integration
def test_preview_schedule_dispatches_empty_availabilities_when_none_exist(
    client: TestClient,
    dispatched_schedule_jobs,
):
    """Should dispatch a job with no availabilities when the user has none."""
    client.post("/api/v1/dev/seed")
    employees = client.get("/api/v1/employees").json()
    for employee in employees:
        availabilities = client.get(
            f"/api/v1/employees/{employee['id']}/availabilities"
        ).json()
        for availability in availabilities:
            client.delete(
                f"/api/v1/employees/{employee['id']}/availabilities/{availability['id']}"
            )

    weeks = client.get("/api/v1/weeks").json()
    week_id = weeks[0]["id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    response = client.post("/api/v1/preview-schedule", json={"shift_vector": shifts})

    assert response.status_code == 202
    assert response.json()["status"] == "processing"
    assert len(dispatched_schedule_jobs[0].payload.availabilities) == 0


@pytest.mark.integration
def test_read_schedule_generation_job_not_found(client: TestClient):
    """Should return 404 when the schedule generation job does not exist."""
    response = client.get(
        "/api/v1/schedule-generation-jobs/00000000-0000-0000-0000-000000000999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Schedule generation job not found"


@pytest.mark.integration
def test_schedule_generation_callback_updates_job_with_valid_signature(
    client: TestClient,
    seeded_data,
    dispatched_schedule_jobs,
):
    """Should update the job result when a valid signed callback is received."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts},
    )
    job_id = preview_response.json()["job_id"]

    raw_body = json.dumps(
        {
            "job_id": job_id,
            "status": "done",
            "result": {"possible": False, "schedule": None},
            "error": None,
        }
    ).encode("utf-8")

    callback_response = client.post(
        "/api/v1/internal/schedule-generation-results",
        content=raw_body,
        headers=_build_signed_callback_headers(raw_body),
    )

    assert callback_response.status_code == 200
    assert callback_response.json() == {
        "job_id": job_id,
        "status": "done",
        "result": {"possible": False, "schedule": None},
        "error": None,
    }

    job_response = client.get(f"/api/v1/schedule-generation-jobs/{job_id}")
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "done"
    assert job_response.json()["result"] == {"possible": False, "schedule": None}
    assert len(dispatched_schedule_jobs) == 1


@pytest.mark.integration
def test_schedule_generation_callback_rejects_invalid_signature(
    client: TestClient,
    seeded_data,
    dispatched_schedule_jobs,
):
    """Should reject callbacks signed with the wrong secret."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts},
    )
    job_id = preview_response.json()["job_id"]

    raw_body = json.dumps(
        {
            "job_id": job_id,
            "status": "done",
            "result": {"possible": True, "schedule": {"shifts": []}},
            "error": None,
        }
    ).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Timestamp": str(int(time.time())),
        "X-Signature": "sha256=invalid",
    }

    callback_response = client.post(
        "/api/v1/internal/schedule-generation-results",
        content=raw_body,
        headers=headers,
    )

    assert callback_response.status_code == 401
    assert callback_response.json()["detail"] == "invalid callback signature"
    assert len(dispatched_schedule_jobs) == 1

    job_response = client.get(f"/api/v1/schedule-generation-jobs/{job_id}")
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "processing"


@pytest.mark.integration
def test_schedule_generation_callback_is_idempotent_for_same_payload(
    client: TestClient,
    seeded_data,
    dispatched_schedule_jobs,
):
    """Should accept the same callback payload more than once without changing the result."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts},
    )
    job_id = preview_response.json()["job_id"]

    raw_body = json.dumps(
        {
            "job_id": job_id,
            "status": "done",
            "result": {"possible": False, "schedule": None},
            "error": None,
        }
    ).encode("utf-8")
    headers = _build_signed_callback_headers(raw_body)

    first_response = client.post(
        "/api/v1/internal/schedule-generation-results",
        content=raw_body,
        headers=headers,
    )
    second_response = client.post(
        "/api/v1/internal/schedule-generation-results",
        content=raw_body,
        headers=headers,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json() == second_response.json()
    assert len(dispatched_schedule_jobs) == 1


@pytest.mark.integration
def test_preview_schedule_marks_job_failed_when_dispatch_fails(
    client: TestClient,
    seeded_data,
    monkeypatch,
):
    """Should mark the job as failed when dispatching to the generator fails."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    def failing_dispatch(_dispatch_request):
        raise RuntimeError("unable to dispatch schedule generation job")

    monkeypatch.setattr(
        schedule_service,
        "dispatch_schedule_generation_job",
        failing_dispatch,
    )

    response = client.post("/api/v1/preview-schedule", json={"shift_vector": shifts})

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "failed"

    job_response = client.get(f"/api/v1/schedule-generation-jobs/{data['job_id']}")
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "failed"
    assert job_response.json()["error"] == "unable to dispatch schedule generation job"
