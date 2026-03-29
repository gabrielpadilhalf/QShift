from fastapi.testclient import TestClient
from datetime import timedelta
import pytest


def next_monday(d=None):
    """Return the next Monday from given date (or today)."""
    from datetime import date
    if d is None:
        d = date.today()
    days_ahead = (7 - d.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return d + timedelta(days=days_ahead)


@pytest.mark.integration
def test_employee_cascade_delete_availabilities(client: TestClient, seeded_data):
    """Should cascade delete availabilities when employee is deleted."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={"weekday": 5, "start_time": "09:00", "end_time": "17:00"},
    )

    availabilities_before = client.get(
        f"/api/v1/employees/{employee_id}/availabilities"
    ).json()
    assert len(availabilities_before) > 0

    delete_response = client.delete(f"/api/v1/employees/{employee_id}")
    assert delete_response.status_code == 204

    availabilities_after = client.get(
        f"/api/v1/employees/{employee_id}/availabilities"
    )
    assert availabilities_after.status_code == 404


@pytest.mark.integration
def test_employee_cascade_delete_assignments(client: TestClient, seeded_data):
    """Should cascade delete assignments when employee is deleted."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    employee_id = employees[0]["id"]
    shift_id = shifts[0]["id"]

    client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={"shifts": [{"shift_id": shift_id, "employee_ids": [employee_id]}]},
    )

    schedule_before = client.get(f"/api/v1/weeks/{week_id}/schedule").json()
    shift_before = next(s for s in schedule_before["shifts"] if s["shift_id"] == shift_id)
    assert len(shift_before["employees"]) > 0

    delete_response = client.delete(f"/api/v1/employees/{employee_id}")
    assert delete_response.status_code == 204

    schedule_after = client.get(f"/api/v1/weeks/{week_id}/schedule").json()
    shift_after = next(s for s in schedule_after["shifts"] if s["shift_id"] == shift_id)
    assert not any(e["employee_id"] == employee_id for e in shift_after["employees"])


@pytest.mark.integration
def test_week_cascade_delete_shifts(client: TestClient, seeded_data):
    """Should cascade delete shifts when week is deleted."""
    week_id = seeded_data["week_id"]

    shifts_before = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    assert len(shifts_before) > 0

    delete_response = client.delete(f"/api/v1/weeks/{week_id}")
    assert delete_response.status_code == 204

    shifts_after = client.get(f"/api/v1/weeks/{week_id}/shifts")
    assert shifts_after.status_code == 404


@pytest.mark.integration
def test_shift_cascade_delete_assignments(client: TestClient, seeded_data):
    """Should cascade delete assignments when shift is deleted."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    shift_id = shifts[0]["id"]
    employee_id = employees[0]["id"]

    client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={"shifts": [{"shift_id": shift_id, "employee_ids": [employee_id]}]},
    )

    schedule_before = client.get(f"/api/v1/weeks/{week_id}/schedule").json()
    shift_before = next(s for s in schedule_before["shifts"] if s["shift_id"] == shift_id)
    assert len(shift_before["employees"]) > 0

    delete_response = client.delete(f"/api/v1/weeks/{week_id}/shifts/{shift_id}")
    assert delete_response.status_code == 204

    schedule_after = client.get(f"/api/v1/weeks/{week_id}/schedule").json()
    assert not any(s["shift_id"] == shift_id for s in schedule_after["shifts"])


@pytest.mark.integration
def test_duplicate_week_same_start_date(client: TestClient, seeded_data):
    """Should reject duplicate week with same start_date."""
    monday = next_monday() + timedelta(days=84)

    first_response = client.post(
        "/api/v1/weeks",
        json={"start_date": monday.isoformat(), "open_days": [0, 1, 2]},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/weeks",
        json={"start_date": monday.isoformat(), "open_days": [3, 4, 5]},
    )
    assert second_response.status_code == 400


@pytest.mark.integration
def test_duplicate_shift_same_slot(client: TestClient, seeded_data):
    """Should reject duplicate shift in same time slot."""
    week_id = seeded_data["week_id"]

    shift_data = {
        "weekday": 4,
        "start_time": "15:00",
        "end_time": "19:00",
        "min_staff": 2,
    }

    first_response = client.post(
        f"/api/v1/weeks/{week_id}/shifts",
        json=shift_data,
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/weeks/{week_id}/shifts",
        json=shift_data,
    )
    assert second_response.status_code == 400


@pytest.mark.integration
def test_duplicate_availability_same_slot(client: TestClient, seeded_data):
    """Should reject duplicate availability in same time slot."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    availability_data = {
        "weekday": 5,
        "start_time": "08:00",
        "end_time": "16:00",
    }

    first_response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json=availability_data,
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json=availability_data,
    )
    assert second_response.status_code == 400


@pytest.mark.integration
def test_assignment_with_inactive_employee(client: TestClient, seeded_data):
    """Should allow assignment of inactive employee."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Inactive Employee", "active": False},
    )
    inactive_employee_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={
            "shifts": [
                {"shift_id": shifts[0]["id"], "employee_ids": [inactive_employee_id]}
            ]
        },
    )

    assert response.status_code == 201


@pytest.mark.integration
def test_assignment_without_availability(client: TestClient, seeded_data):
    """Should allow manual assignment even without availability."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    create_response = client.post(
        "/api/v1/employees",
        json={"name": "No Availability Employee", "active": True},
    )
    employee_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={"shifts": [{"shift_id": shifts[0]["id"], "employee_ids": [employee_id]}]},
    )

    assert response.status_code == 201


@pytest.mark.integration
def test_preview_excludes_inactive_employees(
    client: TestClient,
    seeded_data,
    dispatched_schedule_jobs,
):
    """Should exclude inactive employees from the dispatched generation payload."""
    week_id = seeded_data["week_id"]
    employees = client.get("/api/v1/employees").json()

    for emp in employees:
        client.patch(f"/api/v1/employees/{emp['id']}", json={"active": False})

    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts},
    )

    assert response.status_code == 202
    assert response.json()["status"] == "processing"
    assert dispatched_schedule_jobs[0].payload.employees == []
    assert dispatched_schedule_jobs[0].payload.availabilities == []


@pytest.mark.integration
def test_shift_weekday_not_in_week_open_days(client: TestClient, seeded_data):
    """Should allow creating shift even if weekday not in week open_days."""
    week_id = seeded_data["week_id"]
    week = client.get(f"/api/v1/weeks/{week_id}").json()

    closed_weekday = next(d for d in range(7) if d not in week["open_days"])

    response = client.post(
        f"/api/v1/weeks/{week_id}/shifts",
        json={
            "weekday": closed_weekday,
            "start_time": "09:00",
            "end_time": "17:00",
            "min_staff": 1,
        },
    )

    assert response.status_code == 201


@pytest.mark.integration
def test_multiple_assignments_same_employee_shift(client: TestClient, seeded_data):
    """Should handle duplicate assignment gracefully."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    employees = client.get("/api/v1/employees").json()

    shift_id = shifts[0]["id"]
    employee_id = employees[0]["id"]

    first_response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={"shifts": [{"shift_id": shift_id, "employee_ids": [employee_id]}]},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={"shifts": [{"shift_id": shift_id, "employee_ids": [employee_id]}]},
    )

    assert second_response.status_code in [201, 400]


@pytest.mark.integration
def test_empty_schedule_creation(client: TestClient, seeded_data):
    """Should handle empty schedule creation."""
    week_id = seeded_data["week_id"]

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={"shifts": []},
    )

    assert response.status_code == 201


@pytest.mark.integration
def test_schedule_with_empty_employee_list(client: TestClient, seeded_data):
    """Should handle shift with empty employee list."""
    week_id = seeded_data["week_id"]
    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()

    response = client.post(
        f"/api/v1/weeks/{week_id}/schedule",
        json={"shifts": [{"shift_id": shifts[0]["id"], "employee_ids": []}]},
    )

    assert response.status_code == 201


@pytest.mark.integration
def test_large_min_staff_with_few_employees(
    client: TestClient,
    seeded_data,
    dispatched_schedule_jobs,
):
    """Should accept preview job creation even with impossible staffing demand."""
    week_id = seeded_data["week_id"]

    response = client.post(
        f"/api/v1/weeks/{week_id}/shifts",
        json={
            "weekday": 0,
            "start_time": "06:00",
            "end_time": "08:00",
            "min_staff": 100,
        },
    )

    assert response.status_code == 201

    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts}
    )
    assert preview_response.status_code == 202
    assert preview_response.json()["status"] == "processing"
    assert len(dispatched_schedule_jobs) == 1


@pytest.mark.integration
def test_overlapping_shifts_same_day(client: TestClient, seeded_data):
    """Should allow creating overlapping shifts on same day."""
    week_id = seeded_data["week_id"]

    first_response = client.post(
        f"/api/v1/weeks/{week_id}/shifts",
        json={
            "weekday": 0,
            "start_time": "10:00",
            "end_time": "15:00",
            "min_staff": 1,
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/weeks/{week_id}/shifts",
        json={
            "weekday": 0,
            "start_time": "12:00",
            "end_time": "17:00",
            "min_staff": 1,
        },
    )
    assert second_response.status_code == 201


@pytest.mark.integration
def test_overlapping_availabilities_same_day(client: TestClient, seeded_data):
    """Should allow creating overlapping availabilities on same day."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    first_response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={"weekday": 1, "start_time": "08:00", "end_time": "14:00"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={"weekday": 1, "start_time": "12:00", "end_time": "18:00"},
    )
    assert second_response.status_code == 201
