from fastapi.testclient import TestClient
import pytest

from core_api.core.constants import DEMO_EMAIL, DEMO_PASSWORD
import core_api.services.schedule as schedule_service


@pytest.mark.integration
def test_login_triggers_schedule_generator_wakeup(
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

    response = client.post(
        "/api/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert calls == ["called"]
