from fastapi.testclient import TestClient
import pytest
import core_api.services.schedule as schedule_service


@pytest.mark.integration
def test_create_employee_success(client: TestClient, seeded_data):
    """Should create employee with valid data."""
    response = client.post(
        "/api/v1/employees",
        json={"name": "João Silva", "active": True},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "João Silva"
    assert data["active"] is True
    assert "id" in data
    assert "user_id" in data
    assert "Location" in response.headers


@pytest.mark.integration
def test_create_employee_inactive(client: TestClient, seeded_data):
    """Should create inactive employee."""
    response = client.post(
        "/api/v1/employees",
        json={"name": "Maria Santos", "active": False},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Maria Santos"
    assert data["active"] is False


@pytest.mark.integration
def test_create_employee_empty_name(client: TestClient, seeded_data):
    """Should reject employee with empty name."""
    response = client.post(
        "/api/v1/employees",
        json={"name": "   ", "active": True},
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_create_employee_whitespace_only_name(client: TestClient, seeded_data):
    """Should reject employee with whitespace-only name."""
    response = client.post(
        "/api/v1/employees",
        json={"name": "\t\n  ", "active": True},
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_create_employee_name_too_long(client: TestClient, seeded_data):
    """Should reject employee with name exceeding max length."""
    long_name = "A" * 121
    response = client.post(
        "/api/v1/employees",
        json={"name": long_name, "active": True},
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_create_employee_default_active(client: TestClient, seeded_data):
    """Should default active to True when not provided."""
    response = client.post(
        "/api/v1/employees",
        json={"name": "Pedro Costa"},
    )

    assert response.status_code == 201
    assert response.json()["active"] is True


@pytest.mark.integration
def test_list_employees_empty(client: TestClient):
    """Should return empty list when no employees exist."""
    client.post("/api/v1/dev/seed")

    client.delete(f"/api/v1/employees/{client.get('/api/v1/employees').json()[0]['id']}")
    client.delete(f"/api/v1/employees/{client.get('/api/v1/employees').json()[0]['id']}")
    client.delete(f"/api/v1/employees/{client.get('/api/v1/employees').json()[0]['id']}")
    client.delete(f"/api/v1/employees/{client.get('/api/v1/employees').json()[0]['id']}")
    client.delete(f"/api/v1/employees/{client.get('/api/v1/employees').json()[0]['id']}")

    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
def test_list_employees_ordered_by_name(client: TestClient, seeded_data):
    """Should return employees ordered by name."""
    client.post("/api/v1/employees", json={"name": "Zara", "active": True})
    client.post("/api/v1/employees", json={"name": "Alice", "active": True})
    client.post("/api/v1/employees", json={"name": "Bob", "active": True})

    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    employees = response.json()
    names = [emp["name"] for emp in employees]
    assert names == sorted(names)


@pytest.mark.integration
def test_list_employees_triggers_schedule_generator_wakeup(
    client: TestClient, seeded_data, monkeypatch
):
    calls = []

    def fake_wake_schedule_generator():
        calls.append("called")

    monkeypatch.setattr(
        schedule_service,
        "wake_schedule_generator",
        fake_wake_schedule_generator,
    )

    response = client.get("/api/v1/employees")

    assert response.status_code == 200
    assert calls == ["called"]


@pytest.mark.integration
def test_read_employee_success(client: TestClient, seeded_data):
    """Should return employee by id."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Test Employee", "active": True},
    )
    employee_id = create_response.json()["id"]

    response = client.get(f"/api/v1/employees/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == employee_id
    assert data["name"] == "Test Employee"


@pytest.mark.integration
def test_read_employee_not_found(client: TestClient, seeded_data):
    """Should return 404 for non-existent employee."""
    fake_id = "00000000-0000-0000-0000-000000000999"
    response = client.get(f"/api/v1/employees/{fake_id}")

    assert response.status_code == 404


@pytest.mark.integration
def test_read_employee_invalid_uuid(client: TestClient, seeded_data):
    """Should return 422 for invalid UUID format."""
    response = client.get("/api/v1/employees/not-a-uuid")

    assert response.status_code == 422


@pytest.mark.integration
def test_update_employee_name(client: TestClient, seeded_data):
    """Should update employee name."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Old Name", "active": True},
    )
    employee_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}",
        json={"name": "New Name"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["active"] is True


@pytest.mark.integration
def test_update_employee_active_status(client: TestClient, seeded_data):
    """Should update employee active status."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Employee", "active": True},
    )
    employee_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}",
        json={"active": False},
    )

    assert response.status_code == 200
    assert response.json()["active"] is False


@pytest.mark.integration
def test_update_employee_both_fields(client: TestClient, seeded_data):
    """Should update both name and active status."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Old Name", "active": True},
    )
    employee_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}",
        json={"name": "New Name", "active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["active"] is False


@pytest.mark.integration
def test_update_employee_empty_payload(client: TestClient, seeded_data):
    """Should return unchanged employee when payload is empty."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Employee", "active": True},
    )
    employee_id = create_response.json()["id"]
    original_data = create_response.json()

    response = client.patch(f"/api/v1/employees/{employee_id}", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == original_data["name"]
    assert data["active"] == original_data["active"]


@pytest.mark.integration
def test_update_employee_empty_name(client: TestClient, seeded_data):
    """Should reject update with empty name."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Employee", "active": True},
    )
    employee_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}",
        json={"name": "   "},
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_update_employee_not_found(client: TestClient, seeded_data):
    """Should return 404 when updating non-existent employee."""
    fake_id = "00000000-0000-0000-0000-000000000999"
    response = client.patch(
        f"/api/v1/employees/{fake_id}",
        json={"name": "New Name"},
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_delete_employee_success(client: TestClient, seeded_data):
    """Should delete employee successfully."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "To Delete", "active": True},
    )
    employee_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/employees/{employee_id}")

    assert response.status_code == 204

    get_response = client.get(f"/api/v1/employees/{employee_id}")
    assert get_response.status_code == 404


@pytest.mark.integration
def test_delete_employee_not_found(client: TestClient, seeded_data):
    """Should return 404 when deleting non-existent employee."""
    fake_id = "00000000-0000-0000-0000-000000000999"
    response = client.delete(f"/api/v1/employees/{fake_id}")

    assert response.status_code == 404


@pytest.mark.integration
def test_delete_employee_cascades_availabilities(client: TestClient, seeded_data):
    """Should cascade delete employee availabilities."""
    create_response = client.post(
        "/api/v1/employees",
        json={"name": "Employee", "active": True},
    )
    employee_id = create_response.json()["id"]

    client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={"weekday": 0, "start_time": "09:00", "end_time": "17:00"},
    )

    delete_response = client.delete(f"/api/v1/employees/{employee_id}")
    assert delete_response.status_code == 204

    avail_response = client.get(f"/api/v1/employees/{employee_id}/availabilities")
    assert avail_response.status_code == 404
