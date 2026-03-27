from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.api.dependencies import current_user_id
from app.core.constants import DEMO_USER_ID
import app.services.schedule as schedule_service

API_PREFIX = "/api/v1"


@pytest.fixture
def client():
    """HTTP client for testing the API."""

    app.dependency_overrides[current_user_id] = (  # disables authentication for tests
        lambda: DEMO_USER_ID
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_data(client):
    """Populate database with seed data and return metadata."""
    response = client.post(f"{API_PREFIX}/dev/seed")
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def dispatched_schedule_jobs(monkeypatch):
    """Capture schedule generation dispatches without performing network calls."""
    dispatched_jobs = []

    def fake_dispatch(dispatch_request):
        dispatched_jobs.append(dispatch_request)

    monkeypatch.setattr(
        schedule_service,
        "dispatch_schedule_generation_job",
        fake_dispatch,
    )
    return dispatched_jobs
