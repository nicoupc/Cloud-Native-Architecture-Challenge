"""
Tests for SagaMapper - Domain ↔ DynamoDB translation
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from src.infrastructure.persistence.saga_mapper import SagaMapper
from src.domain.payment_saga import PaymentSaga
from src.domain.saga_state import SagaState
from src.domain.value_objects import SagaId, BookingId, Amount, SagaStep


def _create_saga(state=SagaState.STARTED, completed_at=None, steps=None):
    """Helper to create a saga with known values"""
    saga_id = SagaId("11111111-1111-1111-1111-111111111111")
    booking_id = BookingId("booking-mapper-test")
    amount = Amount(value=250.0, currency="EUR")
    now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

    if steps is None:
        steps = [
            SagaStep(name="RESERVE_BOOKING", status="COMPLETED",
                     started_at=now, completed_at=now, retry_count=0),
            SagaStep(name="PROCESS_PAYMENT", status="PENDING",
                     retry_count=0),
        ]

    return PaymentSaga(
        id=saga_id,
        booking_id=booking_id,
        amount=amount,
        state=state,
        steps=steps,
        current_step_index=1,
        created_at=now,
        updated_at=now,
        completed_at=completed_at,
    )


class TestSagaMapperToDynamoDB:
    """Test SagaMapper.to_dynamodb"""

    def test_should_convert_saga_to_dynamodb_item(self):
        """Saga is correctly mapped to a DynamoDB item dict"""
        saga = _create_saga()
        item = SagaMapper.to_dynamodb(saga)

        assert item["PK"] == "SAGA#11111111-1111-1111-1111-111111111111"
        assert item["SK"] == "SAGA#11111111-1111-1111-1111-111111111111"
        assert item["sagaId"] == "11111111-1111-1111-1111-111111111111"
        assert item["bookingId"] == "booking-mapper-test"
        assert item["amount"] == Decimal("250.0")
        assert item["currency"] == "EUR"
        assert item["status"] == "STARTED"
        assert item["currentStepIndex"] == 1

    def test_should_map_steps_correctly(self):
        """Steps are serialized with all fields"""
        saga = _create_saga()
        item = SagaMapper.to_dynamodb(saga)

        assert len(item["steps"]) == 2
        step0 = item["steps"][0]
        assert step0["name"] == "RESERVE_BOOKING"
        assert step0["status"] == "COMPLETED"
        assert step0["retry_count"] == 0
        assert step0["started_at"] is not None
        assert step0["completed_at"] is not None

        step1 = item["steps"][1]
        assert step1["name"] == "PROCESS_PAYMENT"
        assert step1["status"] == "PENDING"
        assert step1["started_at"] is None
        assert step1["completed_at"] is None

    def test_should_handle_optional_completed_at_none(self):
        """completedAt is None when saga is not completed"""
        saga = _create_saga(completed_at=None)
        item = SagaMapper.to_dynamodb(saga)

        assert item["completedAt"] is None

    def test_should_handle_optional_completed_at_set(self):
        """completedAt is an ISO string when saga is completed"""
        completed = datetime(2025, 1, 15, 13, 0, 0, tzinfo=timezone.utc)
        saga = _create_saga(state=SagaState.COMPLETED, completed_at=completed)
        item = SagaMapper.to_dynamodb(saga)

        assert item["completedAt"] == completed.isoformat()

    def test_should_handle_step_error_message(self):
        """Steps with error_message are serialized correctly"""
        now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        steps = [
            SagaStep(name="PROCESS_PAYMENT", status="FAILED",
                     started_at=now, completed_at=now, retry_count=2,
                     error_message="Gateway timeout"),
        ]
        saga = _create_saga(steps=steps)
        item = SagaMapper.to_dynamodb(saga)

        assert item["steps"][0]["error_message"] == "Gateway timeout"
        assert item["steps"][0]["retry_count"] == 2


class TestSagaMapperFromDynamoDB:
    """Test SagaMapper.from_dynamodb"""

    def _make_dynamodb_item(self, status="STARTED", completed_at=None):
        """Helper to create a DynamoDB item dict"""
        now = "2025-01-15T12:00:00+00:00"
        return {
            "PK": "SAGA#22222222-2222-2222-2222-222222222222",
            "SK": "SAGA#22222222-2222-2222-2222-222222222222",
            "sagaId": "22222222-2222-2222-2222-222222222222",
            "bookingId": "booking-from-dynamo",
            "amount": Decimal("300.50"),
            "currency": "USD",
            "status": status,
            "currentStepIndex": 0,
            "steps": [
                {
                    "name": "RESERVE_BOOKING",
                    "status": "PENDING",
                    "retry_count": 0,
                    "error_message": None,
                    "started_at": None,
                    "completed_at": None,
                },
                {
                    "name": "PROCESS_PAYMENT",
                    "status": "COMPLETED",
                    "retry_count": 1,
                    "error_message": None,
                    "started_at": now,
                    "completed_at": now,
                },
            ],
            "createdAt": now,
            "updatedAt": now,
            "completedAt": completed_at,
        }

    def test_should_convert_dynamodb_item_to_saga(self):
        """DynamoDB item is correctly mapped to a PaymentSaga"""
        item = self._make_dynamodb_item()
        saga = SagaMapper.from_dynamodb(item)

        assert saga.id.value == "22222222-2222-2222-2222-222222222222"
        assert saga.booking_id.value == "booking-from-dynamo"
        assert saga.amount.value == 300.50
        assert saga.amount.currency == "USD"
        assert saga.state == SagaState.STARTED
        assert saga.current_step_index == 0

    def test_should_reconstruct_steps(self):
        """Steps are correctly reconstructed from DynamoDB item"""
        item = self._make_dynamodb_item()
        saga = SagaMapper.from_dynamodb(item)

        assert len(saga.steps) == 2
        assert saga.steps[0].name == "RESERVE_BOOKING"
        assert saga.steps[0].status == "PENDING"
        assert saga.steps[0].started_at is None
        assert saga.steps[1].name == "PROCESS_PAYMENT"
        assert saga.steps[1].status == "COMPLETED"
        assert saga.steps[1].retry_count == 1
        assert saga.steps[1].started_at is not None

    def test_should_handle_all_saga_states(self):
        """All SagaState values can be round-tripped"""
        for state in SagaState:
            completed_at = "2025-01-15T13:00:00+00:00" if state in {
                SagaState.COMPLETED, SagaState.FAILED, SagaState.COMPENSATED
            } else None
            item = self._make_dynamodb_item(status=state.value, completed_at=completed_at)
            saga = SagaMapper.from_dynamodb(item)
            assert saga.state == state

    def test_should_handle_optional_completed_at_none(self):
        """completedAt=None maps to saga.completed_at=None"""
        item = self._make_dynamodb_item(completed_at=None)
        saga = SagaMapper.from_dynamodb(item)

        assert saga.completed_at is None

    def test_should_handle_optional_completed_at_set(self):
        """completedAt ISO string maps to datetime"""
        item = self._make_dynamodb_item(
            completed_at="2025-01-15T14:30:00+00:00"
        )
        saga = SagaMapper.from_dynamodb(item)

        assert saga.completed_at is not None
        assert saga.completed_at.year == 2025

    def test_should_handle_step_error_message_from_dynamodb(self):
        """Steps with error_message are reconstructed correctly"""
        item = self._make_dynamodb_item()
        item["steps"][0]["error_message"] = "Connection refused"
        item["steps"][0]["status"] = "FAILED"

        saga = SagaMapper.from_dynamodb(item)
        assert saga.steps[0].error_message == "Connection refused"


class TestSagaMapperRoundTrip:
    """Test that to_dynamodb → from_dynamodb preserves data"""

    def test_round_trip_preserves_saga_data(self):
        """Converting saga→DynamoDB→saga preserves all fields"""
        original = _create_saga()
        item = SagaMapper.to_dynamodb(original)
        restored = SagaMapper.from_dynamodb(item)

        assert restored.id.value == original.id.value
        assert restored.booking_id.value == original.booking_id.value
        assert restored.amount.value == original.amount.value
        assert restored.amount.currency == original.amount.currency
        assert restored.state == original.state
        assert restored.current_step_index == original.current_step_index
        assert len(restored.steps) == len(original.steps)
        assert restored.completed_at == original.completed_at
