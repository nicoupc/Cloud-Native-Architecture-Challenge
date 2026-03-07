"""
Saga Mapper - Domain ↔ DynamoDB translation

Maps between domain objects and DynamoDB items.
Keeps domain layer pure and independent of infrastructure.
"""

from datetime import datetime
from typing import Dict, Any

from ...domain.payment_saga import PaymentSaga
from ...domain.value_objects import SagaId, BookingId, Amount, SagaStep
from ...domain.saga_state import SagaState


class SagaMapper:
    """Maps PaymentSaga to/from DynamoDB items"""
    
    @staticmethod
    def to_dynamodb(saga: PaymentSaga) -> Dict[str, Any]:
        """
        Convert domain PaymentSaga to DynamoDB item
        
        Args:
            saga: Domain saga object
            
        Returns:
            DynamoDB item dictionary
        """
        return {
            "PK": f"SAGA#{saga.saga_id.value}",
            "SK": f"SAGA#{saga.saga_id.value}",
            "sagaId": saga.saga_id.value,
            "bookingId": saga.booking_id.value,
            "amount": saga.amount.value,
            "currency": saga.amount.currency,
            "status": saga.status.value,
            "currentStepIndex": saga.current_step_index,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "attempts": step.attempts,
                    "lastError": step.last_error,
                    "executedAt": step.executed_at.isoformat() if step.executed_at else None
                }
                for step in saga.steps
            ],
            "createdAt": saga.created_at.isoformat(),
            "updatedAt": saga.updated_at.isoformat(),
            "completedAt": saga.completed_at.isoformat() if saga.completed_at else None,
            "metadata": saga.metadata
        }
    
    @staticmethod
    def from_dynamodb(item: Dict[str, Any]) -> PaymentSaga:
        """
        Convert DynamoDB item to domain PaymentSaga
        
        Args:
            item: DynamoDB item dictionary
            
        Returns:
            Domain saga object
        """
        # Reconstruct value objects
        saga_id = SagaId(item["sagaId"])
        booking_id = BookingId(item["bookingId"])
        amount = Amount(item["amount"], item["currency"])
        status = SagaState(item["status"])
        
        # Reconstruct steps
        steps = [
            SagaStep(
                name=step_data["name"],
                status=step_data["status"],
                attempts=step_data["attempts"],
                last_error=step_data.get("lastError"),
                executed_at=datetime.fromisoformat(step_data["executedAt"]) if step_data.get("executedAt") else None
            )
            for step_data in item["steps"]
        ]
        
        # Create saga instance
        saga = PaymentSaga(
            saga_id=saga_id,
            booking_id=booking_id,
            amount=amount
        )
        
        # Restore state
        saga._status = status
        saga._current_step_index = item["currentStepIndex"]
        saga._steps = steps
        saga._created_at = datetime.fromisoformat(item["createdAt"])
        saga._updated_at = datetime.fromisoformat(item["updatedAt"])
        saga._completed_at = datetime.fromisoformat(item["completedAt"]) if item.get("completedAt") else None
        saga._metadata = item.get("metadata", {})
        
        return saga
