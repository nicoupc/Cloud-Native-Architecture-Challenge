"""
Data Transfer Objects for REST API

Request and response models for API endpoints.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class StartSagaRequest(BaseModel):
    """Request to start a payment saga"""
    booking_id: str = Field(..., description="Booking identifier")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "550e8400-e29b-41d4-a716-446655440000",
                "amount": 100.00,
                "currency": "USD"
            }
        }


class SagaStepResponse(BaseModel):
    """Saga step information"""
    name: str
    status: str
    attempts: int
    last_error: Optional[str] = None
    executed_at: Optional[datetime] = None


class SagaResponse(BaseModel):
    """Saga state response"""
    saga_id: str
    booking_id: str
    amount: float
    currency: str
    status: str
    current_step_index: int
    steps: List[SagaStepResponse]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "saga_id": "660e8400-e29b-41d4-a716-446655440000",
                "booking_id": "550e8400-e29b-41d4-a716-446655440000",
                "amount": 100.00,
                "currency": "USD",
                "status": "COMPLETED",
                "current_step_index": 4,
                "steps": [
                    {
                        "name": "RESERVE_BOOKING",
                        "status": "COMPLETED",
                        "attempts": 1,
                        "last_error": None,
                        "executed_at": "2026-03-07T20:00:00Z"
                    }
                ],
                "created_at": "2026-03-07T20:00:00Z",
                "updated_at": "2026-03-07T20:01:00Z",
                "completed_at": "2026-03-07T20:01:00Z",
                "metadata": {}
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "SagaNotFound",
                "detail": "Saga with ID 123 not found"
            }
        }


class PaginatedSagasResponse(BaseModel):
    """Paginated list of sagas"""
    sagas: List[SagaResponse]
    next_page_token: Optional[str] = None
    count: int
