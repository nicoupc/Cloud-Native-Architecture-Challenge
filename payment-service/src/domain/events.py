"""
Domain Events

Events represent things that have happened in the domain.
They are immutable and carry all necessary information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .value_objects import SagaId, BookingId, Amount


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events
    
    All domain events are immutable and timestamped.
    """
    
    event_id: str
    occurred_at: datetime
    event_type: str
    
    def to_dict(self) -> dict:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "occurred_at": self.occurred_at.isoformat(),
            "event_type": self.event_type,
        }


@dataclass(frozen=True)
class SagaStarted(DomainEvent):
    """
    Event: Saga has been started
    
    Published when a new payment saga is initiated.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    amount: Amount
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
            "amount": self.amount.value,
            "currency": self.amount.currency,
        })
        return base


@dataclass(frozen=True)
class BookingReserved(DomainEvent):
    """
    Event: Booking has been reserved
    
    Published when the first step (reserve booking) completes successfully.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
        })
        return base


@dataclass(frozen=True)
class PaymentProcessed(DomainEvent):
    """
    Event: Payment has been processed successfully
    
    Published when payment gateway confirms the payment.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    amount: Amount
    payment_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
            "amount": self.amount.value,
            "currency": self.amount.currency,
            "payment_id": self.payment_id,
        })
        return base


@dataclass(frozen=True)
class PaymentFailed(DomainEvent):
    """
    Event: Payment processing failed
    
    Published when payment gateway rejects the payment.
    Triggers compensation.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    amount: Amount
    error_message: str
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
            "amount": self.amount.value,
            "currency": self.amount.currency,
            "error_message": self.error_message,
        })
        return base


@dataclass(frozen=True)
class BookingConfirmed(DomainEvent):
    """
    Event: Booking has been confirmed
    
    Published when booking service confirms the booking.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
        })
        return base


@dataclass(frozen=True)
class SagaCompleted(DomainEvent):
    """
    Event: Saga completed successfully
    
    Published when all saga steps complete successfully.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
        })
        return base


@dataclass(frozen=True)
class SagaFailed(DomainEvent):
    """
    Event: Saga failed
    
    Published when saga fails and cannot be recovered.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    error_message: str
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
            "error_message": self.error_message,
        })
        return base


@dataclass(frozen=True)
class SagaCompensating(DomainEvent):
    """
    Event: Saga is compensating (rolling back)
    
    Published when saga starts compensation due to failure.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    reason: str
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
            "reason": self.reason,
        })
        return base


@dataclass(frozen=True)
class SagaCompensated(DomainEvent):
    """
    Event: Saga compensation completed
    
    Published when all compensation steps complete.
    """
    
    saga_id: SagaId
    booking_id: BookingId
    
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "saga_id": str(self.saga_id),
            "booking_id": str(self.booking_id),
        })
        return base
