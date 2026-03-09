"""
Value Objects - Immutable domain primitives

Value objects encapsulate validation and business rules.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class SagaId:
    """
    Saga Identifier
    
    Uniquely identifies a saga instance.
    Immutable and validated.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "SagaId":
        """Generate a new unique saga ID"""
        return cls(value=str(uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> "SagaId":
        """
        Create from string with validation
        
        Args:
            value: UUID string
            
        Returns:
            SagaId instance
            
        Raises:
            ValueError: If value is not a valid UUID
        """
        try:
            # Validate UUID format
            UUID(value)
            return cls(value=value)
        except ValueError as e:
            raise ValueError(f"Invalid saga ID format: {value}") from e
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BookingId:
    """
    Booking Identifier
    
    References a booking in the Booking Service.
    """
    
    value: str
    
    @classmethod
    def from_string(cls, value: str) -> "BookingId":
        """Create from string with validation"""
        if not value or not value.strip():
            raise ValueError("Booking ID cannot be empty")
        return cls(value=value.strip())
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Amount:
    """
    Money Amount
    
    Represents monetary value with validation.
    """
    
    value: float
    currency: str = "USD"
    
    def __post_init__(self):
        """Validate amount"""
        if self.value < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code (e.g., USD)")
    
    def __str__(self) -> str:
        return f"{self.value:.2f} {self.currency}"


@dataclass(frozen=True)
class SagaStep:
    """
    Saga Step
    
    Represents a single step in the saga execution.
    Tracks step name, status, and execution details.
    """
    
    name: str
    status: str  # PENDING, COMPLETED, FAILED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        """Validate step"""
        if not self.name or not self.name.strip():
            raise ValueError("Step name cannot be empty")
        
        valid_statuses = {"PENDING", "COMPLETED", "FAILED"}
        if self.status not in valid_statuses:
            raise ValueError(
                f"Invalid step status: {self.status}. "
                f"Must be one of {valid_statuses}"
            )
    
    @classmethod
    def create_pending(cls, name: str) -> "SagaStep":
        """Create a new pending step"""
        return cls(
            name=name,
            status="PENDING",
            started_at=None,
            completed_at=None,
            retry_count=0,
        )
    
    def mark_started(self) -> "SagaStep":
        """Mark step as started"""
        return SagaStep(
            name=self.name,
            status=self.status,
            started_at=datetime.now(timezone.utc),
            completed_at=self.completed_at,
            error_message=self.error_message,
            retry_count=self.retry_count,
        )
    
    def mark_completed(self) -> "SagaStep":
        """Mark step as completed"""
        return SagaStep(
            name=self.name,
            status="COMPLETED",
            started_at=self.started_at,
            completed_at=datetime.now(timezone.utc),
            error_message=None,
            retry_count=self.retry_count,
        )
    
    def mark_failed(self, error_message: str) -> "SagaStep":
        """Mark step as failed"""
        return SagaStep(
            name=self.name,
            status="FAILED",
            started_at=self.started_at,
            completed_at=datetime.now(timezone.utc),
            error_message=error_message,
            retry_count=self.retry_count,
        )
    
    def increment_retry(self) -> "SagaStep":
        """Increment retry count"""
        return SagaStep(
            name=self.name,
            status=self.status,
            started_at=self.started_at,
            completed_at=self.completed_at,
            error_message=self.error_message,
            retry_count=self.retry_count + 1,
        )
