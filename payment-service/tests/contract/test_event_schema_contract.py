"""
Contract Tests: Payment Service Event Schemas

Verify that events published by the Payment Service conform to the
expected schema that downstream consumers (Notification, Booking) expect.
"""
import pytest
from datetime import datetime, timezone

from src.domain.events import (
    SagaStarted,
    BookingReserved,
    PaymentProcessed,
    PaymentFailed,
    BookingConfirmed,
    SagaCompleted,
    SagaFailed,
    SagaCompensating,
    SagaCompensated,
    DomainEvent,
)
from src.domain.value_objects import SagaId, BookingId, Amount


def _make_base_kwargs():
    return {
        "event_id": "evt-001",
        "occurred_at": datetime.now(timezone.utc),
    }


def _sid(v="s1"):
    return SagaId(value=v)


def _bid(v="b1"):
    return BookingId(value=v)


def _amt(v=50.0, currency="USD"):
    return Amount(value=v, currency=currency)


class TestDomainEventBaseContract:
    """All domain events must have the base fields."""

    @pytest.mark.parametrize(
        "event_cls,extra",
        [
            (SagaStarted, {"saga_id": _sid(), "booking_id": _bid(), "amount": _amt(), "event_type": "SagaStarted"}),
            (BookingReserved, {"saga_id": _sid(), "booking_id": _bid(), "event_type": "BookingReserved"}),
            (PaymentProcessed, {"saga_id": _sid(), "booking_id": _bid(), "amount": _amt(), "payment_id": "p1", "event_type": "PaymentProcessed"}),
            (PaymentFailed, {"saga_id": _sid(), "booking_id": _bid(), "amount": _amt(), "error_message": "fail", "event_type": "PaymentFailed"}),
            (BookingConfirmed, {"saga_id": _sid(), "booking_id": _bid(), "event_type": "BookingConfirmed"}),
            (SagaCompleted, {"saga_id": _sid(), "booking_id": _bid(), "event_type": "SagaCompleted"}),
            (SagaFailed, {"saga_id": _sid(), "booking_id": _bid(), "error_message": "fail", "event_type": "SagaFailed"}),
            (SagaCompensating, {"saga_id": _sid(), "booking_id": _bid(), "reason": "undo", "event_type": "SagaCompensating"}),
            (SagaCompensated, {"saga_id": _sid(), "booking_id": _bid(), "event_type": "SagaCompensated"}),
        ],
    )
    def test_base_fields_present(self, event_cls, extra):
        """Every event must carry event_id, occurred_at, and event_type."""
        event = event_cls(**_make_base_kwargs(), **extra)
        assert hasattr(event, "event_id")
        assert hasattr(event, "occurred_at")
        assert hasattr(event, "event_type")

    @pytest.mark.parametrize(
        "event_cls,extra",
        [
            (SagaStarted, {"saga_id": _sid(), "booking_id": _bid(), "amount": _amt(), "event_type": "SagaStarted"}),
            (PaymentProcessed, {"saga_id": _sid(), "booking_id": _bid(), "amount": _amt(), "payment_id": "p1", "event_type": "PaymentProcessed"}),
        ],
    )
    def test_to_dict_returns_serializable(self, event_cls, extra):
        """to_dict() must produce a JSON-serializable dict with required keys."""
        import json

        event = event_cls(**_make_base_kwargs(), **extra)
        d = event.to_dict()
        assert isinstance(d, dict)
        json.dumps(d)  # must not raise
        assert "event_id" in d
        assert "occurred_at" in d
        assert "event_type" in d


class TestSagaStartedContract:
    """SagaStarted event must carry saga_id, booking_id, and amount."""

    def test_required_fields(self):
        event = SagaStarted(
            **_make_base_kwargs(),
            event_type="SagaStarted",
            saga_id=_sid("saga-123"),
            booking_id=_bid("booking-456"),
            amount=_amt(50.0),
        )
        assert str(event.saga_id) == "saga-123"
        assert str(event.booking_id) == "booking-456"
        assert event.amount.value == 50.0

    def test_to_dict_includes_saga_fields(self):
        event = SagaStarted(
            **_make_base_kwargs(),
            event_type="SagaStarted",
            saga_id=_sid("saga-123"),
            booking_id=_bid("booking-456"),
            amount=_amt(50.0),
        )
        d = event.to_dict()
        assert d["saga_id"] == "saga-123"
        assert d["booking_id"] == "booking-456"
        assert d["amount"] == 50.0


class TestPaymentProcessedContract:
    """PaymentProcessed must include amount and payment_id."""

    def test_required_fields(self):
        event = PaymentProcessed(
            **_make_base_kwargs(),
            event_type="PaymentProcessed",
            saga_id=_sid("saga-1"),
            booking_id=_bid("booking-1"),
            amount=_amt(75.0),
            payment_id="pay-001",
        )
        assert event.amount.value == 75.0
        assert event.payment_id == "pay-001"
        assert isinstance(event.amount.value, (int, float))

    def test_to_dict_includes_payment_fields(self):
        event = PaymentProcessed(
            **_make_base_kwargs(),
            event_type="PaymentProcessed",
            saga_id=_sid("saga-1"),
            booking_id=_bid("booking-1"),
            amount=_amt(75.0),
            payment_id="pay-001",
        )
        d = event.to_dict()
        assert "amount" in d
        assert "payment_id" in d


class TestPaymentFailedContract:
    """PaymentFailed must include error_message."""

    def test_required_fields(self):
        event = PaymentFailed(
            **_make_base_kwargs(),
            event_type="PaymentFailed",
            saga_id=_sid("saga-1"),
            booking_id=_bid("booking-1"),
            amount=_amt(50.0),
            error_message="Insufficient funds",
        )
        assert event.error_message == "Insufficient funds"
        assert isinstance(event.error_message, str)

    def test_to_dict_includes_error_message(self):
        event = PaymentFailed(
            **_make_base_kwargs(),
            event_type="PaymentFailed",
            saga_id=_sid("saga-1"),
            booking_id=_bid("booking-1"),
            amount=_amt(50.0),
            error_message="Card declined",
        )
        d = event.to_dict()
        assert "error_message" in d
        assert d["error_message"] == "Card declined"


class TestSagaCompletedContract:
    """SagaCompleted must have saga_id and booking_id."""

    def test_required_fields(self):
        event = SagaCompleted(
            **_make_base_kwargs(),
            event_type="SagaCompleted",
            saga_id=_sid("saga-1"),
            booking_id=_bid("booking-1"),
        )
        assert str(event.saga_id) == "saga-1"
        assert str(event.booking_id) == "booking-1"


class TestSagaCompensatingContract:
    """SagaCompensating must include reason."""

    def test_required_fields(self):
        event = SagaCompensating(
            **_make_base_kwargs(),
            event_type="SagaCompensating",
            saga_id=_sid("saga-1"),
            booking_id=_bid("booking-1"),
            reason="Payment failed",
        )
        assert event.reason == "Payment failed"
        assert isinstance(event.reason, str)


class TestEventTypeValidity:
    """Event types must be from the known set."""

    def test_event_types_are_valid_strings(self):
        valid_types = {
            "SagaStarted", "BookingReserved", "PaymentProcessed", "PaymentFailed",
            "BookingConfirmed", "SagaCompleted", "SagaFailed",
            "SagaCompensating", "SagaCompensated",
        }
        events = [
            SagaStarted(**_make_base_kwargs(), event_type="SagaStarted", saga_id=_sid(), booking_id=_bid(), amount=_amt(1)),
            PaymentProcessed(**_make_base_kwargs(), event_type="PaymentProcessed", saga_id=_sid(), booking_id=_bid(), amount=_amt(1), payment_id="p"),
            PaymentFailed(**_make_base_kwargs(), event_type="PaymentFailed", saga_id=_sid(), booking_id=_bid(), amount=_amt(1), error_message="e"),
            SagaCompleted(**_make_base_kwargs(), event_type="SagaCompleted", saga_id=_sid(), booking_id=_bid()),
        ]
        for event in events:
            assert event.event_type in valid_types


class TestTimestampContract:
    """Timestamps must be ISO 8601 serializable."""

    def test_occurred_at_is_datetime(self):
        event = SagaStarted(
            **_make_base_kwargs(),
            event_type="SagaStarted",
            saga_id=_sid(),
            booking_id=_bid(),
            amount=_amt(1),
        )
        assert isinstance(event.occurred_at, datetime)

    def test_to_dict_timestamp_is_iso_string(self):
        event = SagaStarted(
            **_make_base_kwargs(),
            event_type="SagaStarted",
            saga_id=_sid(),
            booking_id=_bid(),
            amount=_amt(1),
        )
        d = event.to_dict()
        ts = d["occurred_at"]
        assert isinstance(ts, str)
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
