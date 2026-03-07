"""
Tests for PaymentSaga Aggregate Root
"""

import pytest
from src.domain.payment_saga import PaymentSaga
from src.domain.saga_state import SagaState
from src.domain.value_objects import BookingId, Amount
from src.domain.exceptions import (
    InvalidSagaStateTransitionError,
    SagaAlreadyCompletedError,
)


class TestPaymentSagaCreation:
    """Test PaymentSaga creation"""
    
    def test_create_new_saga(self):
        """Test creating a new saga"""
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=100.0)
        
        saga = PaymentSaga.create(booking_id=booking_id, amount=amount)
        
        assert saga.id is not None
        assert saga.booking_id == booking_id
        assert saga.amount == amount
        assert saga.state == SagaState.STARTED
        assert len(saga.steps) == 4  # 4 steps defined
        assert saga.current_step_index == 0
        assert saga.completed_at is None
    
    def test_saga_has_correct_steps(self):
        """Test that saga is created with correct steps"""
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=100.0)
        
        saga = PaymentSaga.create(booking_id=booking_id, amount=amount)
        
        step_names = [step.name for step in saga.steps]
        assert "RESERVE_BOOKING" in step_names
        assert "PROCESS_PAYMENT" in step_names
        assert "CONFIRM_BOOKING" in step_names
        assert "SEND_NOTIFICATION" in step_names


class TestPaymentSagaStateTransitions:
    """Test saga state transitions"""
    
    def test_transition_to_valid_state(self):
        """Test transitioning to a valid state"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        saga.transition_to(SagaState.BOOKING_RESERVED)
        assert saga.state == SagaState.BOOKING_RESERVED
    
    def test_transition_to_invalid_state_raises_error(self):
        """Test that invalid transition raises error"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        with pytest.raises(InvalidSagaStateTransitionError):
            saga.transition_to(SagaState.COMPLETED)  # Can't skip states
    
    def test_transition_from_completed_raises_error(self):
        """Test that transitioning from completed state raises error"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        # Transition to completed
        saga.transition_to(SagaState.BOOKING_RESERVED)
        saga.transition_to(SagaState.PAYMENT_PROCESSED)
        saga.transition_to(SagaState.BOOKING_CONFIRMED)
        saga.transition_to(SagaState.COMPLETED)
        
        # Try to transition again
        with pytest.raises(SagaAlreadyCompletedError):
            saga.transition_to(SagaState.STARTED)
    
    def test_transition_updates_timestamp(self):
        """Test that transition updates updated_at"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        original_updated_at = saga.updated_at
        saga.transition_to(SagaState.BOOKING_RESERVED)
        
        assert saga.updated_at > original_updated_at
    
    def test_transition_to_terminal_state_sets_completed_at(self):
        """Test that terminal state sets completed_at"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        saga.transition_to(SagaState.FAILED)
        assert saga.completed_at is not None


class TestPaymentSagaStepExecution:
    """Test saga step execution"""
    
    def test_start_current_step(self):
        """Test starting current step"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        saga.start_current_step()
        current_step = saga.get_current_step()
        
        assert current_step is not None
        assert current_step.started_at is not None
    
    def test_complete_current_step(self):
        """Test completing current step"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        assert saga.current_step_index == 0
        saga.complete_current_step()
        
        assert saga.current_step_index == 1
        assert saga.steps[0].status == "COMPLETED"
    
    def test_fail_current_step(self):
        """Test failing current step"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        error_msg = "Payment gateway timeout"
        saga.fail_current_step(error_msg)
        
        current_step = saga.get_current_step()
        assert current_step.status == "FAILED"
        assert current_step.error_message == error_msg
        assert saga.error_message == error_msg
    
    def test_retry_current_step(self):
        """Test retrying current step"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        current_step = saga.get_current_step()
        assert current_step.retry_count == 0
        
        saga.retry_current_step()
        current_step = saga.get_current_step()
        assert current_step.retry_count == 1
    
    def test_get_current_step_returns_none_when_all_completed(self):
        """Test that get_current_step returns None when all steps completed"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        # Complete all steps
        for _ in range(len(saga.steps)):
            saga.complete_current_step()
        
        assert saga.get_current_step() is None


class TestPaymentSagaQueries:
    """Test saga query methods"""
    
    def test_is_completed(self):
        """Test is_completed method"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        assert not saga.is_completed()
        
        saga.transition_to(SagaState.BOOKING_RESERVED)
        saga.transition_to(SagaState.PAYMENT_PROCESSED)
        saga.transition_to(SagaState.BOOKING_CONFIRMED)
        saga.transition_to(SagaState.COMPLETED)
        
        assert saga.is_completed()
    
    def test_is_failed(self):
        """Test is_failed method"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        assert not saga.is_failed()
        
        saga.transition_to(SagaState.FAILED)
        assert saga.is_failed()
    
    def test_is_compensated(self):
        """Test is_compensated method"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        assert not saga.is_compensated()
        
        saga.transition_to(SagaState.BOOKING_RESERVED)
        saga.transition_to(SagaState.COMPENSATING)
        saga.transition_to(SagaState.COMPENSATED)
        
        assert saga.is_compensated()
    
    def test_requires_compensation(self):
        """Test requires_compensation method"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        assert not saga.requires_compensation()
        
        saga.transition_to(SagaState.BOOKING_RESERVED)
        assert saga.requires_compensation()
        
        saga.transition_to(SagaState.COMPENSATING)
        assert saga.requires_compensation()
    
    def test_get_completed_steps(self):
        """Test getting completed steps"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        assert len(saga.get_completed_steps()) == 0
        
        saga.complete_current_step()
        assert len(saga.get_completed_steps()) == 1
        
        saga.complete_current_step()
        assert len(saga.get_completed_steps()) == 2
    
    def test_str_representation(self):
        """Test string representation"""
        saga = PaymentSaga.create(
            booking_id=BookingId.from_string("booking-123"),
            amount=Amount(value=100.0)
        )
        
        str_repr = str(saga)
        assert "PaymentSaga" in str_repr
        assert "booking-123" in str_repr
        assert "STARTED" in str_repr
