"""
Payment Saga - Aggregate Root

Orchestrates the distributed payment transaction.
Maintains saga state and enforces business rules.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from .saga_state import SagaState, SagaStateTransition
from .value_objects import SagaId, BookingId, Amount, SagaStep
from .exceptions import (
    InvalidSagaStateTransitionError,
    SagaAlreadyCompletedError,
)


@dataclass
class PaymentAttempt:
    """Records a single payment attempt"""
    attempt_number: int
    timestamp: datetime
    status: str  # SUCCESS, FAILED
    payment_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PaymentSaga:
    """
    Payment Saga Aggregate Root
    
    Represents a distributed payment transaction across multiple services.
    Implements the Saga Pattern with orchestration.
    
    Responsibilities:
    - Maintain saga state
    - Enforce state transitions
    - Track execution steps
    - Manage compensation
    """
    
    id: SagaId
    booking_id: BookingId
    amount: Amount
    state: SagaState
    steps: List[SagaStep] = field(default_factory=list)
    current_step_index: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    payment_id: Optional[str] = None
    payment_attempts: List['PaymentAttempt'] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        booking_id: BookingId,
        amount: Amount,
    ) -> "PaymentSaga":
        """
        Factory method: Create a new saga
        
        Args:
            booking_id: ID of the booking to process
            amount: Payment amount
            
        Returns:
            New PaymentSaga in STARTED state
        """
        # Define saga steps
        steps = [
            SagaStep.create_pending("RESERVE_BOOKING"),
            SagaStep.create_pending("PROCESS_PAYMENT"),
            SagaStep.create_pending("CONFIRM_BOOKING"),
            SagaStep.create_pending("SEND_NOTIFICATION"),
        ]
        
        return cls(
            id=SagaId.generate(),
            booking_id=booking_id,
            amount=amount,
            state=SagaState.STARTED,
            steps=steps,
            current_step_index=0,
        )
    
    def transition_to(self, new_state: SagaState) -> None:
        """
        Transition to a new state
        
        Args:
            new_state: Target state
            
        Raises:
            InvalidSagaStateTransitionError: If transition is invalid
            SagaAlreadyCompletedError: If saga is already completed
        """
        # Check if saga is already in terminal state
        if SagaStateTransition.is_terminal_state(self.state):
            raise SagaAlreadyCompletedError(str(self.id))
        
        # Validate transition
        SagaStateTransition.validate_transition(self.state, new_state)
        
        # Update state
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc)
        
        # Mark as completed if terminal state
        if SagaStateTransition.is_terminal_state(new_state):
            self.completed_at = datetime.now(timezone.utc)
    
    def start_current_step(self) -> None:
        """Mark current step as started"""
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            self.steps[self.current_step_index] = step.mark_started()
            self.updated_at = datetime.now(timezone.utc)
    
    def complete_current_step(self) -> None:
        """
        Mark current step as completed and advance
        
        Raises:
            IndexError: If no more steps
        """
        if self.current_step_index >= len(self.steps):
            raise IndexError("No more steps to complete")
        
        # Mark step as completed
        step = self.steps[self.current_step_index]
        self.steps[self.current_step_index] = step.mark_completed()
        
        # Advance to next step
        self.current_step_index += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def fail_current_step(self, error_message: str) -> None:
        """
        Mark current step as failed
        
        Args:
            error_message: Error description
        """
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            self.steps[self.current_step_index] = step.mark_failed(error_message)
        
        self.error_message = error_message
        self.updated_at = datetime.now(timezone.utc)
    
    def retry_current_step(self) -> None:
        """Increment retry count for current step"""
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            self.steps[self.current_step_index] = step.increment_retry()
            self.updated_at = datetime.now(timezone.utc)
    
    def get_current_step(self) -> Optional[SagaStep]:
        """Get the current step being executed"""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def is_completed(self) -> bool:
        """Check if saga is completed successfully"""
        return self.state == SagaState.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if saga has failed"""
        return self.state == SagaState.FAILED
    
    def is_compensated(self) -> bool:
        """Check if saga has been compensated"""
        return self.state == SagaState.COMPENSATED
    
    def requires_compensation(self) -> bool:
        """Check if saga requires compensation"""
        return self.state in {
            SagaState.COMPENSATING,
            SagaState.BOOKING_RESERVED,
            SagaState.PAYMENT_PROCESSED,
        }
    
    def get_completed_steps(self) -> List[SagaStep]:
        """Get list of completed steps (for compensation)"""
        return [step for step in self.steps if step.status == "COMPLETED"]
    
    def set_payment_id(self, payment_id: str) -> None:
        """Store the payment gateway's payment ID"""
        self.payment_id = payment_id
        self.updated_at = datetime.now(timezone.utc)
    
    def record_payment_attempt(self, status: str, payment_id: Optional[str] = None, error: Optional[str] = None) -> None:
        """Record a payment attempt"""
        attempt = PaymentAttempt(
            attempt_number=len(self.payment_attempts) + 1,
            timestamp=datetime.now(timezone.utc),
            status=status,
            payment_id=payment_id,
            error=error,
        )
        self.payment_attempts.append(attempt)
        self.updated_at = datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        return (
            f"PaymentSaga(id={self.id}, "
            f"booking_id={self.booking_id}, "
            f"state={self.state}, "
            f"step={self.current_step_index}/{len(self.steps)})"
        )
