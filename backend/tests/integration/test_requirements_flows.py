from fastapi.testclient import TestClient
import pytest


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


@pytest.mark.integration
def test_rf001_register_availability_flow(client: TestClient, seeded_data):
    """
    RF001: Registrar disponibilidade dos funcionários.
    
    Fluxo completo:
    1. Criar funcionário
    2. Registrar disponibilidade (dias e horários)
    3. Verificar resposta HTTP
    4. Ler disponibilidade do banco de dados
    5. Confirmar persistência (NF001) e consistência (NF002)
    """
    employee_response = client.post(
        "/api/v1/employees",
        json={"name": "João Silva", "active": True},
    )
    assert employee_response.status_code == 201
    employee_id = employee_response.json()["id"]

    availability_response = client.post(
        f"/api/v1/employees/{employee_id}/availabilities",
        json={
            "weekday": 0,
            "start_time": "09:00",
            "end_time": "18:00",
        },
    )

    assert availability_response.status_code == 201
    assert "Location" in availability_response.headers

    availability_data = availability_response.json()
    assert availability_data["weekday"] == 0
    assert availability_data["start_time"] == "09:00:00"
    assert availability_data["end_time"] == "18:00:00"
    assert availability_data["employee_id"] == employee_id

    availability_id = availability_data["id"]

    read_response = client.get(f"/api/v1/employees/{employee_id}/availabilities")
    assert read_response.status_code == 200

    availabilities = read_response.json()
    saved_availability = next(
        (a for a in availabilities if a["id"] == availability_id), None
    )
    assert saved_availability is not None
    assert saved_availability["weekday"] == 0
    assert saved_availability["start_time"] == "09:00:00"
    assert saved_availability["end_time"] == "18:00:00"


@pytest.mark.integration
def test_rf005_generate_schedule_flow(client: TestClient, dispatched_schedule_jobs):
    """
    RF005: Gerar automaticamente escalas semanais.
    
    Fluxo completo:
    1. Criar funcionários
    2. Registrar disponibilidades
    3. Criar semana (RF002 - dias de funcionamento)
    4. Criar turnos (RF003 - horários, RF004 - quantidade mínima)
    5. Criar job assíncrono de geração
    6. Verificar que o payload enviado ao gerador está correto
    7. Consultar o status do job criado
    """
    client.post("/api/v1/dev/seed")

    employees = client.get("/api/v1/employees").json()
    assert len(employees) == 5

    for emp in employees:
        availabilities = client.get(
            f"/api/v1/employees/{emp['id']}/availabilities"
        ).json()
        assert len(availabilities) > 0

    weeks = client.get("/api/v1/weeks").json()
    assert len(weeks) > 0
    week_id = weeks[0]["id"]
    week = weeks[0]
    assert len(week["open_days"]) > 0

    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    assert len(shifts) > 0
    for shift in shifts:
        assert shift["min_staff"] >= 1

    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts}
    )
    assert preview_response.status_code == 202

    preview_data = preview_response.json()
    assert preview_data["status"] == "processing"
    assert "job_id" in preview_data

    assert len(dispatched_schedule_jobs) == 1
    dispatch_request = dispatched_schedule_jobs[0]
    assert str(dispatch_request.job_id) == preview_data["job_id"]
    assert (
        dispatch_request.payload.model_dump(mode="json")["shift_vector"]
        == _normalize_preview_shift_vector(shifts)
    )
    assert len(dispatch_request.payload.employees) == len(employees)
    assert len(dispatch_request.payload.availabilities) > 0

    job_response = client.get(
        f"/api/v1/schedule-generation-jobs/{preview_data['job_id']}"
    )
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "processing"
    assert job_response.json()["result"] is None
    assert job_response.json()["error"] is None


@pytest.mark.integration
def test_rf008_notify_unavailability_flow(client: TestClient, dispatched_schedule_jobs):
    """
    RF008: Notificar indisponibilidade de funcionários.
    
    Fluxo completo:
    1. Criar cenário com funcionários insuficientes
    2. Tentar gerar escala
    3. Verificar que o payload enviado ao gerador reflete ausência de funcionários
    4. Confirmar que a API aceita o job assíncrono
    5. Verificar consistência do sistema (NF002)
    """
    client.post("/api/v1/dev/seed")

    employees = client.get("/api/v1/employees").json()
    for emp in employees:
        client.delete(f"/api/v1/employees/{emp['id']}")

    weeks = client.get("/api/v1/weeks").json()
    week_id = weeks[0]["id"]

    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    assert len(shifts) > 0

    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts}
    )
    assert preview_response.status_code == 202

    preview_data = preview_response.json()
    assert preview_data["status"] == "processing"
    assert dispatched_schedule_jobs[0].payload.employees == []
    assert dispatched_schedule_jobs[0].payload.availabilities == []


@pytest.mark.integration
def test_rf008_notify_unavailability_insufficient_staff(
    client: TestClient,
    dispatched_schedule_jobs,
):
    """
    RF008: Notificar indisponibilidade - cenário de staff insuficiente.
    
    Cenário: Funcionários disponíveis, mas sem disponibilidade para turnos específicos.
    """
    client.post("/api/v1/dev/seed")

    employees = client.get("/api/v1/employees").json()
    for emp in employees:
        availabilities = client.get(
            f"/api/v1/employees/{emp['id']}/availabilities"
        ).json()
        for avail in availabilities:
            client.delete(
                f"/api/v1/employees/{emp['id']}/availabilities/{avail['id']}"
            )

    weeks = client.get("/api/v1/weeks").json()
    week_id = weeks[0]["id"]

    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts}
    )
    assert preview_response.status_code == 202

    preview_data = preview_response.json()
    assert preview_data["status"] == "processing"
    assert dispatched_schedule_jobs[0].payload.availabilities == []


@pytest.mark.integration
def test_rf008_notify_unavailability_inactive_employees(
    client: TestClient,
    dispatched_schedule_jobs,
):
    """
    RF008: Notificar indisponibilidade - cenário de funcionários inativos.
    
    Cenário: Todos os funcionários marcados como inativos.
    """
    client.post("/api/v1/dev/seed")

    employees = client.get("/api/v1/employees").json()
    for emp in employees:
        client.patch(f"/api/v1/employees/{emp['id']}", json={"active": False})

    weeks = client.get("/api/v1/weeks").json()
    week_id = weeks[0]["id"]

    shifts = client.get(f"/api/v1/weeks/{week_id}/shifts").json()
    preview_response = client.post(
        "/api/v1/preview-schedule",
        json={"shift_vector": shifts}
    )
    assert preview_response.status_code == 202

    preview_data = preview_response.json()
    assert preview_data["status"] == "processing"
    assert dispatched_schedule_jobs[0].payload.employees == []
    assert dispatched_schedule_jobs[0].payload.availabilities == []
