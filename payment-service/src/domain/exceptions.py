"""
Domain Exceptions

Business rule violations and domain errors.
"""

from typing import Any


class DomainException(Exception):
    """Base exception for domain errors"""
    pass


class InvalidSagaStateTransitionError(DomainException):
    """Raised when attempting an invalid state transition"""
    
    def __init__(self, from_state: Any, to_state: Any):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid saga state transition: {from_state} -> {to_state}"
        )


class SagaNotFoundException(DomainException):
    """Raised when saga is not found"""
    
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        super().__init__(f"Saga not found: {saga_id}")


class SagaAlreadyCompletedError(DomainException):
    """Raised when trying to modify a completed saga"""
    
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        super().__init__(f"Saga already completed: {saga_id}")


class InvalidSagaStepError(DomainException):
    """Raised when saga step is invalid"""
    
    def __init__(self, message: str):
        super().__init__(message)
