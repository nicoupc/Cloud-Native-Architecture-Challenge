"""
Saga Controller - REST API endpoints

Provides HTTP endpoints for saga management.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends

from ...application.saga_orchestrator import SagaOrchestrator
from ...domain.value_objects import SagaId, BookingId, Amount
from ...domain.exceptions import SagaNotFoundException
from .dto import (
    StartSagaRequest,
    SagaResponse,
    SagaStepResponse,
    ErrorResponse,
    PaginatedSagasResponse
)


router = APIRouter(prefix="/api/v1/sagas", tags=["sagas"])


def get_orchestrator() -> SagaOrchestrator:
    """
    Dependency injection for SagaOrchestrator
    
    In production: Use proper DI container
    For now: Will be set by main.py
    """
    # This will be injected by FastAPI dependency system
    # Configured in main.py
    pass


def saga_to_response(saga) -> SagaResponse:
    """Convert domain saga to response DTO"""
    return SagaResponse(
        saga_id=saga.saga_id.value,
        booking_id=saga.booking_id.value,
        amount=saga.amount.value,
        currency=saga.amount.currency,
        status=saga.status.value,
        current_step_index=saga.current_step_index,
        steps=[
            SagaStepResponse(
                name=step.name,
                status=step.status,
                attempts=step.attempts,
                last_error=step.last_error,
                executed_at=step.executed_at
            )
            for step in saga.steps
        ],
        created_at=saga.created_at,
        updated_at=saga.updated_at,
        completed_at=saga.completed_at,
        metadata=saga.metadata
    )


@router.post(
    "",
    response_model=SagaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new payment saga",
    responses={
        201: {"description": "Saga started successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def start_saga(
    request: StartSagaRequest,
    orchestrator: SagaOrchestrator = Depends(get_orchestrator)
) -> SagaResponse:
    """
    Start a new payment saga
    
    Initiates the saga orchestration process for a booking payment.
    The saga will coordinate multiple steps across services.
    """
    try:
        booking_id = BookingId(request.booking_id)
        amount = Amount(request.amount, request.currency)
        
        saga = await orchestrator.start_saga(booking_id, amount)
        
        return saga_to_response(saga)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start saga: {str(e)}"
        )


@router.get(
    "/{saga_id}",
    response_model=SagaResponse,
    summary="Get saga by ID",
    responses={
        200: {"description": "Saga found"},
        404: {"model": ErrorResponse, "description": "Saga not found"}
    }
)
async def get_saga(
    saga_id: str,
    orchestrator: SagaOrchestrator = Depends(get_orchestrator)
) -> SagaResponse:
    """
    Get saga state by ID
    
    Retrieves the current state of a saga including all steps.
    """
    try:
        saga = await orchestrator.get_saga(SagaId(saga_id))
        
        if not saga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Saga {saga_id} not found"
            )
        
        return saga_to_response(saga)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=PaginatedSagasResponse,
    summary="List all sagas",
    responses={
        200: {"description": "List of sagas"}
    }
)
async def list_sagas(
    limit: int = 100,
    page_token: Optional[str] = None,
    orchestrator: SagaOrchestrator = Depends(get_orchestrator)
) -> PaginatedSagasResponse:
    """
    List all sagas with pagination
    
    Returns a paginated list of all sagas in the system.
    """
    try:
        sagas, next_token = await orchestrator.list_sagas(limit, page_token)
        
        return PaginatedSagasResponse(
            sagas=[saga_to_response(saga) for saga in sagas],
            next_page_token=next_token,
            count=len(sagas)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sagas: {str(e)}"
        )


@router.post(
    "/{saga_id}/compensate",
    response_model=SagaResponse,
    summary="Force saga compensation",
    responses={
        200: {"description": "Compensation started"},
        404: {"model": ErrorResponse, "description": "Saga not found"}
    }
)
async def compensate_saga(
    saga_id: str,
    orchestrator: SagaOrchestrator = Depends(get_orchestrator)
) -> SagaResponse:
    """
    Force compensation for a saga
    
    Manually triggers compensation (rollback) for a saga.
    Useful for testing or manual intervention.
    """
    try:
        saga = await orchestrator.get_saga(SagaId(saga_id))
        
        if not saga:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Saga {saga_id} not found"
            )
        
        compensated_saga = await orchestrator.compensate(saga)
        
        return saga_to_response(compensated_saga)
        
    except SagaNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compensate saga: {str(e)}"
        )
