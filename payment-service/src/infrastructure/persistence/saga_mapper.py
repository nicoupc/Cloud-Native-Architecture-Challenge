"""
Saga Mapper - Domain ↔ DynamoDB translation

Maps between domain objects and DynamoDB items.
Keeps domain layer pure and independent of infrastructure.
"""

from datetime import datetime
from decimal import Decimal
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
        """
        return {
            "PK": f"SAGA#{saga.id.value}",
            "SK": f"SAGA#{saga.id.value}",
            "sagaId": saga.id.value,
            "bookingId": saga.booking_id.value,
            "amount": Decimal(str(saga.amount.value)),
            "currency": saga.amount.currency,
            "status": saga.state.value,
            "currentStepIndex": saga.current_step_index,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "retry_count": step.retry_count,
                    "error_message": step.error_message,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                }
                for step in saga.steps
            ],
            "createdAt": saga.created_at.isoformat(),
            "updatedAt": saga.updated_at.isoformat(),
            "completedAt": saga.completed_at.isoformat() if saga.completed_at else None,
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
        amount = Amount(float(item["amount"]), item["currency"])
        status = SagaState(item["status"])
        
        # Reconstruct steps
        steps = [
            SagaStep(
                name=step_data["name"],
                status=step_data["status"],
                retry_count=int(step_data.get("retry_count", 0)),
                error_message=step_data.get("error_message"),
                started_at=datetime.fromisoformat(step_data["started_at"]) if step_data.get("started_at") else None,
                completed_at=datetime.fromisoformat(step_data["completed_at"]) if step_data.get("completed_at") else None,
            )
            for step_data in item["steps"]
        ]
        
        # Create saga instance restoring full state
        saga = PaymentSaga(
            id=saga_id,
            booking_id=booking_id,
            amount=amount,
            state=status,
            steps=steps,
            current_step_index=int(item["currentStepIndex"]),
            created_at=datetime.fromisoformat(item["createdAt"]),
            updated_at=datetime.fromisoformat(item["updatedAt"]),
            completed_at=datetime.fromisoformat(item["completedAt"]) if item.get("completedAt") else None,
        )
        
        return saga
