"""
Saga State - State Machine for Payment Saga

Defines all possible states and valid transitions for the saga.
"""

from enum import Enum
from typing import Set


class SagaState(str, Enum):
    """
    Saga State Machine
    
    States represent the current position in the saga execution.
    Each state has specific valid transitions.
    """
    
    # Initial state
    STARTED = "STARTED"
    
    # Forward execution states
    BOOKING_RESERVED = "BOOKING_RESERVED"
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED"
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    
    # Success state
    COMPLETED = "COMPLETED"
    
    # Failure states
    FAILED = "FAILED"
    
    # Compensation states
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"


class SagaStateTransition:
    """
    Saga State Transition Rules
    
    Defines which state transitions are valid.
    Prevents invalid state changes.
    """
    
    # Valid transitions map
    _VALID_TRANSITIONS: dict[SagaState, Set[SagaState]] = {
        SagaState.STARTED: {
            SagaState.BOOKING_RESERVED,
            SagaState.FAILED,
        },
        SagaState.BOOKING_RESERVED: {
            SagaState.PAYMENT_PROCESSED,
            SagaState.COMPENSATING,
            SagaState.FAILED,
        },
        SagaState.PAYMENT_PROCESSED: {
            SagaState.BOOKING_CONFIRMED,
            SagaState.COMPENSATING,
            SagaState.FAILED,
        },
        SagaState.BOOKING_CONFIRMED: {
            SagaState.COMPLETED,
            SagaState.FAILED,
        },
        SagaState.COMPLETED: set(),  # Terminal state
        SagaState.FAILED: set(),  # Terminal state
        SagaState.COMPENSATING: {
            SagaState.COMPENSATED,
            SagaState.FAILED,
        },
        SagaState.COMPENSATED: set(),  # Terminal state
    }
    
    @classmethod
    def is_valid_transition(
        cls,
        from_state: SagaState,
        to_state: SagaState
    ) -> bool:
        """
        Check if transition is valid
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is valid
        """
        valid_next_states = cls._VALID_TRANSITIONS.get(from_state, set())
        return to_state in valid_next_states
    
    @classmethod
    def validate_transition(
        cls,
        from_state: SagaState,
        to_state: SagaState
    ) -> None:
        """
        Validate transition or raise exception
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Raises:
            InvalidSagaStateTransitionError: If transition is invalid
        """
        if not cls.is_valid_transition(from_state, to_state):
            from ..domain.exceptions import InvalidSagaStateTransitionError
            raise InvalidSagaStateTransitionError(from_state, to_state)
    
    @classmethod
    def is_terminal_state(cls, state: SagaState) -> bool:
        """
        Check if state is terminal (no more transitions)
        
        Args:
            state: State to check
            
        Returns:
            True if state is terminal
        """
        return state in {
            SagaState.COMPLETED,
            SagaState.FAILED,
            SagaState.COMPENSATED,
        }
