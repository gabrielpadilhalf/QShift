from fastapi.testclient import TestClient
import pytest


@pytest.mark.integration
def test_create_availability_success(client: TestClient, seeded_data):
    """Should create availability with valid data."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={
            "weekday": 2,
            "start_time": "10:00",
            "end_time": "16:00",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["weekday"] == 2
    assert data["start_time"] == "10:00:00"
    assert data["end_time"] == "16:00:00"
    assert data["employee_id"] == employee_id
    assert "Location" in response.headers


@pytest.mark.integration
def test_create_availability_end_before_start(client: TestClient, seeded_data):
    """Should reject availability with end_time before start_time."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={
            "weekday": 0,
            "start_time": "18:00",
            "end_time": "12:00",
        },
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_create_availability_end_equals_start(client: TestClient, seeded_data):
    """Should reject availability with end_time equal to start_time."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={
            "weekday": 0,
            "start_time": "12:00",
            "end_time": "12:00",
        },
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_create_availability_invalid_weekday_negative(client: TestClient, seeded_data):
    """Should reject availability with negative weekday."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={
            "weekday": -1,
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_create_availability_invalid_weekday_too_high(client: TestClient, seeded_data):
    """Should reject availability with weekday > 6."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={
            "weekday": 7,
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_create_availability_employee_not_found(client: TestClient, seeded_data):
    """Should return 404 when creating availability for non-existent employee."""
    fake_employee_id = "00000000-0000-0000-0000-000000000999"
    response = client.post(
        f"/api/v1/employees/{fake_employee_id}/availabilities",
        json={
            "weekday": 0,
            "start_time": "09:00",
            "end_time": "17:00",
        },
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_create_availability_duplicate(client: TestClient, seeded_data):
    """Should reject duplicate availability (same employee, weekday, times)."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    availability_data = {
        "weekday": 3,
        "start_time": "08:00",
        "end_time": "12:00",
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
def test_list_availabilities_success(client: TestClient, seeded_data):
    """Should list all availabilities for an employee."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    response = client.get(f"/api/v1/employees/{employee_id}/availabilities")

    assert response.status_code == 200
    availabilities = response.json()
    assert isinstance(availabilities, list)
    assert all(a["employee_id"] == employee_id for a in availabilities)


@pytest.mark.integration
def test_list_availabilities_ordered(client: TestClient, seeded_data):
    """Should return availabilities ordered by weekday and start_time."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    response = client.get(f"/api/v1/employees/{employee_id}/availabilities")

    assert response.status_code == 200
    availabilities = response.json()
    for i in range(len(availabilities) - 1):
        current = availabilities[i]
        next_avail = availabilities[i + 1]
        assert (current["weekday"], current["start_time"]) <= (
            next_avail["weekday"],
            next_avail["start_time"],
        )


@pytest.mark.integration
def test_list_availabilities_employee_not_found(client: TestClient, seeded_data):
    """Should return 404 when listing availabilities for non-existent employee."""
    fake_employee_id = "00000000-0000-0000-0000-000000000999"
    response = client.get(f"/api/v1/employees/{fake_employee_id}/availabilities")

    assert response.status_code == 404


@pytest.mark.integration
def test_update_availability_times(client: TestClient, seeded_data):
    """Should update availability times."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]
    availabilities = client.get(
        f"/api/v1/employees/{employee_id}/availabilities"
    ).json()
    availability_id = availabilities[0]["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}/availabilities/{availability_id}",
        json={"start_time": "10:00", "end_time": "14:00"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["start_time"] == "10:00:00"
    assert data["end_time"] == "14:00:00"


@pytest.mark.integration
def test_update_availability_weekday(client: TestClient, seeded_data):
    """Should update availability weekday."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]
    availabilities = client.get(
        f"/api/v1/employees/{employee_id}/availabilities"
    ).json()
    availability_id = availabilities[0]["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}/availabilities/{availability_id}",
        json={"weekday": 5},
    )

    assert response.status_code == 200
    assert response.json()["weekday"] == 5


@pytest.mark.integration
def test_update_availability_invalid_times(client: TestClient, seeded_data):
    """Should reject update with invalid times."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]
    availabilities = client.get(
        f"/api/v1/employees/{employee_id}/availabilities"
    ).json()
    availability_id = availabilities[0]["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}/availabilities/{availability_id}",
        json={"start_time": "18:00", "end_time": "12:00"},
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_update_availability_not_found(client: TestClient, seeded_data):
    """Should return 404 when updating non-existent availability."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]
    fake_availability_id = "00000000-0000-0000-0000-000000000999"

    response = client.patch(
        f"/api/v1/employees/{employee_id}/availabilities/{fake_availability_id}",
        json={"start_time": "10:00"},
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_delete_availability_success(client: TestClient, seeded_data):
    """Should delete availability successfully."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]

    create_response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={
            "weekday": 6,
            "start_time": "10:00",
            "end_time": "14:00",
        },
    )
    availability_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/employees/{employee_id}/availabilities/{availability_id}"
    )

    assert response.status_code == 204

    list_response = client.get(f"/api/v1/employees/{employee_id}/availabilities")
    availabilities = list_response.json()
    assert not any(a["id"] == availability_id for a in availabilities)


@pytest.mark.integration
def test_delete_availability_not_found(client: TestClient, seeded_data):
    """Should return 404 when deleting non-existent availability."""
    employees = client.get("/api/v1/employees").json()
    employee_id = employees[0]["id"]
    fake_availability_id = "00000000-0000-0000-0000-000000000999"

    response = client.delete(
        f"/api/v1/employees/{employee_id}/availabilities/{fake_availability_id}"
    )

    assert response.status_code == 404



# ─── Bulk endpoint: GET /employees/availabilities ────────────────────────────


@pytest.mark.integration
def test_get_all_availabilities_returns_all_employees(client: TestClient, seeded_data):
    """GET /employees/availabilities deve retornar as disponibilidades de todos
    os funcionários do usuário autenticado em uma única requisição."""
    employees = client.get("/api/v1/employees").json()
    assert len(employees) > 0

    # Conta o total somando as individuais por funcionário
    total_individual = sum(
        len(client.get(f"/api/v1/employees/{e['id']}/availabilities").json())
        for e in employees
    )

    response = client.get("/api/v1/employees/availabilities")

    assert response.status_code == 200
    all_avails = response.json()
    assert isinstance(all_avails, list)
    assert len(all_avails) == total_individual

    # Cada item deve ter os campos esperados
    for avail in all_avails:
        assert "id" in avail
        assert "employee_id" in avail
        assert "weekday" in avail
        assert "start_time" in avail
        assert "end_time" in avail

    # Todos os employee_ids devem pertencer a funcionários do usuário autenticado
    employee_ids = {e["id"] for e in employees}
    assert all(a["employee_id"] in employee_ids for a in all_avails)


@pytest.mark.integration
def test_get_all_availabilities_empty_when_none_exist(client: TestClient, seeded_data):
    """GET /employees/availabilities deve retornar lista vazia quando nenhuma
    disponibilidade está cadastrada para os funcionários do usuário."""
    employees = client.get("/api/v1/employees").json()
    for emp in employees:
        avails = client.get(f"/api/v1/employees/{emp['id']}/availabilities").json()
        for av in avails:
            client.delete(
                f"/api/v1/employees/{emp['id']}/availabilities/{av['id']}"
            )

    response = client.get("/api/v1/employees/availabilities")

    assert response.status_code == 200
    assert response.json() == []
