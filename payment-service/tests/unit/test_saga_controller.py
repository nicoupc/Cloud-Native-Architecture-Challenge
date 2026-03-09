"""
Tests for SagaController - REST API endpoints
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.infrastructure.api.saga_controller import router, get_orchestrator
from src.domain.payment_saga import PaymentSaga
from src.domain.saga_state import SagaState
from src.domain.value_objects import SagaId, BookingId, Amount, SagaStep
from src.domain.exceptions import SagaNotFoundException


def _create_test_saga(
    saga_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    booking_id="booking-ctrl-test",
    amount=100.0,
    state=SagaState.STARTED,
):
    """Helper to create a saga for controller tests"""
    now = datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    steps = [
        SagaStep(name="RESERVE_BOOKING", status="PENDING", retry_count=0),
        SagaStep(name="PROCESS_PAYMENT", status="PENDING", retry_count=0),
        SagaStep(name="CONFIRM_BOOKING", status="PENDING", retry_count=0),
        SagaStep(name="SEND_NOTIFICATION", status="PENDING", retry_count=0),
    ]
    return PaymentSaga(
        id=SagaId(saga_id),
        booking_id=BookingId(booking_id),
        amount=Amount(value=amount, currency="USD"),
        state=state,
        steps=steps,
        current_step_index=0,
        created_at=now,
        updated_at=now,
        completed_at=None,
    )


@pytest.fixture
def mock_orchestrator():
    """Create a mock SagaOrchestrator"""
    return AsyncMock()


@pytest.fixture
def client(mock_orchestrator):
    """Create a FastAPI TestClient with dependency override"""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    return TestClient(app)


class TestStartSaga:
    """Test POST /api/v1/sagas"""

    def test_should_start_saga_successfully(self, client, mock_orchestrator):
        """201 is returned when saga starts successfully"""
        saga = _create_test_saga()
        mock_orchestrator.start_saga.return_value = saga

        response = client.post(
            "/api/v1/sagas",
            json={"booking_id": "booking-ctrl-test", "amount": 100.0, "currency": "USD"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["saga_id"] == saga.id.value
        assert data["booking_id"] == "booking-ctrl-test"
        assert data["amount"] == 100.0
        assert data["status"] == "STARTED"
        assert len(data["steps"]) == 4

    def test_should_return_400_on_value_error(self, client, mock_orchestrator):
        """400 is returned when orchestrator raises ValueError"""
        mock_orchestrator.start_saga.side_effect = ValueError("Invalid booking ID")

        response = client.post(
            "/api/v1/sagas",
            json={"booking_id": "bad", "amount": 100.0},
        )

        assert response.status_code == 400

    def test_should_return_500_on_unexpected_error(self, client, mock_orchestrator):
        """500 is returned on unexpected errors"""
        mock_orchestrator.start_saga.side_effect = RuntimeError("DB down")

        response = client.post(
            "/api/v1/sagas",
            json={"booking_id": "booking-err", "amount": 50.0},
        )

        assert response.status_code == 500


class TestGetSaga:
    """Test GET /api/v1/sagas/{saga_id}"""

    def test_should_get_saga_by_id(self, client, mock_orchestrator):
        """200 is returned with saga data"""
        saga = _create_test_saga()
        mock_orchestrator.get_saga.return_value = saga

        response = client.get(f"/api/v1/sagas/{saga.id.value}")

        assert response.status_code == 200
        data = response.json()
        assert data["saga_id"] == saga.id.value
        assert data["booking_id"] == "booking-ctrl-test"

    def test_should_return_404_for_unknown_saga(self, client, mock_orchestrator):
        """404 is returned when saga is not found"""
        mock_orchestrator.get_saga.return_value = None

        response = client.get("/api/v1/sagas/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404


class TestListSagas:
    """Test GET /api/v1/sagas"""

    def test_should_list_sagas(self, client, mock_orchestrator):
        """200 is returned with paginated saga list"""
        saga1 = _create_test_saga(saga_id="11111111-1111-1111-1111-111111111111")
        saga2 = _create_test_saga(saga_id="22222222-2222-2222-2222-222222222222")
        mock_orchestrator.list_sagas.return_value = ([saga1, saga2], None)

        response = client.get("/api/v1/sagas")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["sagas"]) == 2
        assert data["next_page_token"] is None

    def test_should_return_empty_list(self, client, mock_orchestrator):
        """200 with empty list when no sagas exist"""
        mock_orchestrator.list_sagas.return_value = ([], None)

        response = client.get("/api/v1/sagas")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["sagas"] == []


class TestCompensateSaga:
    """Test POST /api/v1/sagas/{saga_id}/compensate"""

    def test_should_compensate_saga(self, client, mock_orchestrator):
        """200 is returned when compensation succeeds"""
        saga = _create_test_saga(state=SagaState.BOOKING_RESERVED)
        compensated = _create_test_saga(state=SagaState.COMPENSATED)
        mock_orchestrator.get_saga.return_value = saga
        mock_orchestrator.compensate_saga.return_value = compensated

        response = client.post(f"/api/v1/sagas/{saga.id.value}/compensate")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPENSATED"

    def test_should_return_404_for_unknown_saga_compensation(self, client, mock_orchestrator):
        """404 is returned when saga to compensate is not found"""
        mock_orchestrator.get_saga.return_value = None

        response = client.post("/api/v1/sagas/00000000-0000-0000-0000-000000000000/compensate")

        assert response.status_code == 404

    def test_should_return_500_on_compensation_error(self, client, mock_orchestrator):
        """500 is returned when compensation fails unexpectedly"""
        saga = _create_test_saga()
        mock_orchestrator.get_saga.return_value = saga
        mock_orchestrator.compensate_saga.side_effect = RuntimeError("Compensation failed")

        response = client.post(f"/api/v1/sagas/{saga.id.value}/compensate")

        assert response.status_code == 500
