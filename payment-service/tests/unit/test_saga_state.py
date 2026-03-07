"""
Tests for Saga State Machine
"""

import pytest
from src.domain.saga_state import SagaState, SagaStateTransition
from src.domain.exceptions import InvalidSagaStateTransitionError


class TestSagaState:
    """Test SagaState enum"""
    
    def test_saga_states_exist(self):
        """Test that all required states are defined"""
        assert SagaState.STARTED
        assert SagaState.BOOKING_RESERVED
        assert SagaState.PAYMENT_PROCESSED
        assert SagaState.BOOKING_CONFIRMED
        assert SagaState.COMPLETED
        assert SagaState.FAILED
        assert SagaState.COMPENSATING
        assert SagaState.COMPENSATED


class TestSagaStateTransition:
    """Test Saga State Transitions"""
    
    def test_valid_transition_started_to_booking_reserved(self):
        """Test valid transition: STARTED -> BOOKING_RESERVED"""
        assert SagaStateTransition.is_valid_transition(
            SagaState.STARTED,
            SagaState.BOOKING_RESERVED
        )
    
    def test_valid_transition_booking_reserved_to_payment_processed(self):
        """Test valid transition: BOOKING_RESERVED -> PAYMENT_PROCESSED"""
        assert SagaStateTransition.is_valid_transition(
            SagaState.BOOKING_RESERVED,
            SagaState.PAYMENT_PROCESSED
        )
    
    def test_valid_transition_payment_processed_to_booking_confirmed(self):
        """Test valid transition: PAYMENT_PROCESSED -> BOOKING_CONFIRMED"""
        assert SagaStateTransition.is_valid_transition(
            SagaState.PAYMENT_PROCESSED,
            SagaState.BOOKING_CONFIRMED
        )
    
    def test_valid_transition_booking_confirmed_to_completed(self):
        """Test valid transition: BOOKING_CONFIRMED -> COMPLETED"""
        assert SagaStateTransition.is_valid_transition(
            SagaState.BOOKING_CONFIRMED,
            SagaState.COMPLETED
        )
    
    def test_valid_transition_to_compensating(self):
        """Test valid transition to COMPENSATING from various states"""
        assert SagaStateTransition.is_valid_transition(
            SagaState.BOOKING_RESERVED,
            SagaState.COMPENSATING
        )
        assert SagaStateTransition.is_valid_transition(
            SagaState.PAYMENT_PROCESSED,
            SagaState.COMPENSATING
        )
    
    def test_invalid_transition_completed_to_any(self):
        """Test that COMPLETED is a terminal state"""
        assert not SagaStateTransition.is_valid_transition(
            SagaState.COMPLETED,
            SagaState.STARTED
        )
        assert not SagaStateTransition.is_valid_transition(
            SagaState.COMPLETED,
            SagaState.COMPENSATING
        )
    
    def test_invalid_transition_backward(self):
        """Test that backward transitions are not allowed"""
        assert not SagaStateTransition.is_valid_transition(
            SagaState.PAYMENT_PROCESSED,
            SagaState.BOOKING_RESERVED
        )
        assert not SagaStateTransition.is_valid_transition(
            SagaState.BOOKING_CONFIRMED,
            SagaState.PAYMENT_PROCESSED
        )
    
    def test_validate_transition_success(self):
        """Test validate_transition does not raise for valid transition"""
        # Should not raise
        SagaStateTransition.validate_transition(
            SagaState.STARTED,
            SagaState.BOOKING_RESERVED
        )
    
    def test_validate_transition_failure(self):
        """Test validate_transition raises for invalid transition"""
        with pytest.raises(InvalidSagaStateTransitionError) as exc_info:
            SagaStateTransition.validate_transition(
                SagaState.COMPLETED,
                SagaState.STARTED
            )
        
        assert "COMPLETED" in str(exc_info.value)
        assert "STARTED" in str(exc_info.value)
    
    def test_is_terminal_state(self):
        """Test terminal state detection"""
        assert SagaStateTransition.is_terminal_state(SagaState.COMPLETED)
        assert SagaStateTransition.is_terminal_state(SagaState.FAILED)
        assert SagaStateTransition.is_terminal_state(SagaState.COMPENSATED)
        
        assert not SagaStateTransition.is_terminal_state(SagaState.STARTED)
        assert not SagaStateTransition.is_terminal_state(SagaState.BOOKING_RESERVED)
        assert not SagaStateTransition.is_terminal_state(SagaState.COMPENSATING)
