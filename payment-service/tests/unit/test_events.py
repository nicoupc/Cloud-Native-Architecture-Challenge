"""
Tests for Domain Events
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

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
)
from src.domain.value_objects import SagaId, BookingId, Amount


class TestDomainEvents:
    """Test domain events"""
    
    def test_saga_started_event(self):
        """Test SagaStarted event creation"""
        saga_id = SagaId.generate()
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=100.0)
        
        event = SagaStarted(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="SagaStarted",
            saga_id=saga_id,
            booking_id=booking_id,
            amount=amount,
        )
        
        assert event.saga_id == saga_id
        assert event.booking_id == booking_id
        assert event.amount == amount
        assert event.event_type == "SagaStarted"
    
    def test_saga_started_to_dict(self):
        """Test SagaStarted serialization"""
        saga_id = SagaId.generate()
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=100.0)
        
        event = SagaStarted(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="SagaStarted",
            saga_id=saga_id,
            booking_id=booking_id,
            amount=amount,
        )
        
        event_dict = event.to_dict()
        
        assert "saga_id" in event_dict
        assert "booking_id" in event_dict
        assert "amount" in event_dict
        assert event_dict["amount"] == 100.0
        assert event_dict["currency"] == "USD"
    
    def test_payment_processed_event(self):
        """Test PaymentProcessed event"""
        saga_id = SagaId.generate()
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=50.0)
        
        event = PaymentProcessed(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="PaymentProcessed",
            saga_id=saga_id,
            booking_id=booking_id,
            amount=amount,
            payment_id="payment-456",
        )
        
        assert event.payment_id == "payment-456"
        assert event.amount.value == 50.0
    
    def test_payment_failed_event(self):
        """Test PaymentFailed event"""
        saga_id = SagaId.generate()
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=75.0)
        
        event = PaymentFailed(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="PaymentFailed",
            saga_id=saga_id,
            booking_id=booking_id,
            amount=amount,
            error_message="Card declined",
        )
        
        assert event.error_message == "Card declined"
        
        event_dict = event.to_dict()
        assert event_dict["error_message"] == "Card declined"
    
    def test_saga_compensating_event(self):
        """Test SagaCompensating event"""
        saga_id = SagaId.generate()
        booking_id = BookingId.from_string("booking-123")
        
        event = SagaCompensating(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="SagaCompensating",
            saga_id=saga_id,
            booking_id=booking_id,
            reason="Payment gateway timeout",
        )
        
        assert event.reason == "Payment gateway timeout"
        
        event_dict = event.to_dict()
        assert "reason" in event_dict
    
    def test_events_are_immutable(self):
        """Test that events are immutable"""
        saga_id = SagaId.generate()
        booking_id = BookingId.from_string("booking-123")
        
        event = BookingReserved(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="BookingReserved",
            saga_id=saga_id,
            booking_id=booking_id,
        )
        
        # Events should be frozen (immutable)
        with pytest.raises(Exception):  # FrozenInstanceError
            event.saga_id = SagaId.generate()  # type: ignore
    
    def test_all_events_have_base_fields(self):
        """Test that all events have required base fields"""
        saga_id = SagaId.generate()
        booking_id = BookingId.from_string("booking-123")
        
        events = [
            SagaStarted(
                event_id=str(uuid4()),
                occurred_at=datetime.now(timezone.utc),
                event_type="SagaStarted",
                saga_id=saga_id,
                booking_id=booking_id,
                amount=Amount(value=100.0),
            ),
            BookingReserved(
                event_id=str(uuid4()),
                occurred_at=datetime.now(timezone.utc),
                event_type="BookingReserved",
                saga_id=saga_id,
                booking_id=booking_id,
            ),
            SagaCompleted(
                event_id=str(uuid4()),
                occurred_at=datetime.now(timezone.utc),
                event_type="SagaCompleted",
                saga_id=saga_id,
                booking_id=booking_id,
            ),
        ]
        
        for event in events:
            assert event.event_id
            assert event.occurred_at
            assert event.event_type
            
            # All should be serializable
            event_dict = event.to_dict()
            assert "event_id" in event_dict
            assert "occurred_at" in event_dict
            assert "event_type" in event_dict
