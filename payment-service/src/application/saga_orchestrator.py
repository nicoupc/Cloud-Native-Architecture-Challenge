"""
Saga Orchestrator - Coordinates saga execution

The orchestrator is responsible for:
- Starting sagas
- Executing steps in sequence
- Handling failures and triggering compensation
- Publishing domain events
"""

import logging
from typing import Optional, List
from uuid import uuid4
from datetime import datetime, timezone

from ..domain.payment_saga import PaymentSaga
from ..domain.saga_state import SagaState
from ..domain.value_objects import SagaId, BookingId, Amount
from ..domain.ports import (
    SagaRepository,
    EventPublisher,
    PaymentGateway,
    BookingServiceClient,
    NotificationServiceClient,
    PaymentGatewayError,
    BookingServiceError,
)
from ..domain.events import (
    SagaStarted,
    BookingReserved,
    PaymentProcessed,
    PaymentFailed,
    BookingConfirmed,
    SagaCompleted,
    SagaFailed,
    SagaCompensating,
    SagaCompensated,
)
from ..domain.exceptions import SagaNotFoundException

logger = logging.getLogger(__name__)


class SagaOrchestrator:
    """
    Saga Orchestrator
    
    Coordinates the execution of payment sagas.
    Implements the orchestration pattern (centralized coordination).
    
    Responsibilities:
    - Start new sagas
    - Execute saga steps sequentially
    - Handle step failures
    - Trigger compensation on failure
    - Publish domain events
    """
    
    def __init__(
        self,
        saga_repository: SagaRepository,
        event_publisher: EventPublisher,
        payment_gateway: PaymentGateway,
        booking_service: BookingServiceClient,
        notification_service: NotificationServiceClient,
        max_retries: int = 3,
    ):
        self.saga_repository = saga_repository
        self.event_publisher = event_publisher
        self.payment_gateway = payment_gateway
        self.booking_service = booking_service
        self.notification_service = notification_service
        self.max_retries = max_retries
    
    async def start_saga(
        self,
        booking_id: BookingId,
        amount: Amount,
    ) -> PaymentSaga:
        """
        Start a new payment saga
        
        Args:
            booking_id: Booking to process
            amount: Payment amount
            
        Returns:
            Created saga
        """
        logger.info(f"Starting saga for booking {booking_id}")
        
        # Create saga
        saga = PaymentSaga.create(
            booking_id=booking_id,
            amount=amount,
        )
        
        # Persist saga
        saga = await self.saga_repository.save(saga)
        
        # Publish event
        event = SagaStarted(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="SagaStarted",
            saga_id=saga.id,
            booking_id=saga.booking_id,
            amount=saga.amount,
        )
        await self.event_publisher.publish(event)
        
        logger.info(f"Saga {saga.id} started successfully")
        
        # Start executing steps
        await self.execute_saga(saga.id)
        
        return saga
    
    async def execute_saga(self, saga_id: SagaId) -> PaymentSaga:
        """
        Execute saga steps sequentially
        
        Args:
            saga_id: Saga to execute
            
        Returns:
            Updated saga
            
        Raises:
            SagaNotFoundException: If saga not found
        """
        logger.info(f"Executing saga {saga_id}")
        
        # Load saga
        saga = await self.saga_repository.find_by_id(saga_id)
        if not saga:
            raise SagaNotFoundException(str(saga_id))
        
        # Execute steps until completion or failure
        while not saga.is_completed() and not saga.is_failed():
            current_step = saga.get_current_step()
            
            if not current_step:
                # All steps completed
                await self._complete_saga(saga)
                break
            
            logger.info(
                f"Executing step {current_step.name} "
                f"for saga {saga_id}"
            )
            
            try:
                # Execute step
                await self._execute_step(saga, current_step.name)
                
                # Mark step as completed
                saga.complete_current_step()
                saga = await self.saga_repository.save(saga)
                
            except Exception as e:
                logger.error(
                    f"Step {current_step.name} failed for saga {saga_id}: {e}"
                )
                
                # Check if we should retry
                if current_step.retry_count < self.max_retries:
                    saga.retry_current_step()
                    saga = await self.saga_repository.save(saga)
                    logger.info(
                        f"Retrying step {current_step.name} "
                        f"(attempt {current_step.retry_count + 1})"
                    )
                    continue
                
                # Max retries exceeded, fail step
                saga.fail_current_step(str(e))
                saga = await self.saga_repository.save(saga)
                
                # Trigger compensation
                await self.compensate_saga(saga, str(e))
                break
        
        return saga
    
    async def _execute_step(self, saga: PaymentSaga, step_name: str) -> None:
        """
        Execute a single saga step
        
        Args:
            saga: Saga being executed
            step_name: Name of step to execute
            
        Raises:
            Exception: If step execution fails
        """
        if step_name == "RESERVE_BOOKING":
            await self._reserve_booking(saga)
        elif step_name == "PROCESS_PAYMENT":
            await self._process_payment(saga)
        elif step_name == "CONFIRM_BOOKING":
            await self._confirm_booking(saga)
        elif step_name == "SEND_NOTIFICATION":
            await self._send_notification(saga)
        else:
            raise ValueError(f"Unknown step: {step_name}")
    
    async def _reserve_booking(self, saga: PaymentSaga) -> None:
        """
        Step 1: Reserve booking
        
        This step is actually already done by Booking Service.
        We just transition state and publish event.
        """
        logger.info(f"Reserving booking {saga.booking_id}")
        
        # Transition state
        saga.transition_to(SagaState.BOOKING_RESERVED)
        await self.saga_repository.save(saga)
        
        # Publish event
        event = BookingReserved(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="BookingReserved",
            saga_id=saga.id,
            booking_id=saga.booking_id,
        )
        await self.event_publisher.publish(event)
    
    async def _process_payment(self, saga: PaymentSaga) -> None:
        """
        Step 2: Process payment through payment gateway
        
        Raises:
            PaymentGatewayError: If payment fails
        """
        logger.info(f"Processing payment for booking {saga.booking_id}")
        
        try:
            # Call payment gateway
            result = await self.payment_gateway.process_payment(
                booking_id=saga.booking_id,
                amount=saga.amount,
            )
            
            payment_id = result.get("payment_id")
            
            # Store payment_id and record successful attempt
            if payment_id:
                saga.set_payment_id(payment_id)
            saga.record_payment_attempt(
                status="SUCCESS",
                payment_id=payment_id,
            )
            
            # Transition state
            saga.transition_to(SagaState.PAYMENT_PROCESSED)
            await self.saga_repository.save(saga)
            
            # Publish success event
            event = PaymentProcessed(
                event_id=str(uuid4()),
                occurred_at=datetime.now(timezone.utc),
                event_type="PaymentProcessed",
                saga_id=saga.id,
                booking_id=saga.booking_id,
                amount=saga.amount,
                payment_id=payment_id,
            )
            await self.event_publisher.publish(event)
            
        except PaymentGatewayError as e:
            saga.record_payment_attempt(
                status="FAILED",
                error=str(e),
            )
            # Publish failure event
            event = PaymentFailed(
                event_id=str(uuid4()),
                occurred_at=datetime.now(timezone.utc),
                event_type="PaymentFailed",
                saga_id=saga.id,
                booking_id=saga.booking_id,
                amount=saga.amount,
                error_message=str(e),
            )
            await self.event_publisher.publish(event)
            raise
    
    async def _confirm_booking(self, saga: PaymentSaga) -> None:
        """
        Step 3: Confirm booking in Booking Service
        
        Raises:
            BookingServiceError: If confirmation fails
        """
        logger.info(f"Confirming booking {saga.booking_id}")
        
        # Call booking service
        await self.booking_service.confirm_booking(saga.booking_id)
        
        # Transition state
        saga.transition_to(SagaState.BOOKING_CONFIRMED)
        await self.saga_repository.save(saga)
        
        # Publish event
        event = BookingConfirmed(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="BookingConfirmed",
            saga_id=saga.id,
            booking_id=saga.booking_id,
        )
        await self.event_publisher.publish(event)
    
    async def _send_notification(self, saga: PaymentSaga) -> None:
        """
        Step 4: Send confirmation notification
        """
        logger.info(f"Sending notification for booking {saga.booking_id}")
        
        # Send notification
        await self.notification_service.send_payment_confirmation(
            booking_id=saga.booking_id,
            amount=saga.amount,
        )
    
    async def _complete_saga(self, saga: PaymentSaga) -> None:
        """
        Mark saga as completed
        
        Args:
            saga: Saga to complete
        """
        logger.info(f"Completing saga {saga.id}")
        
        # Transition to completed
        saga.transition_to(SagaState.COMPLETED)
        await self.saga_repository.save(saga)
        
        # Publish event
        event = SagaCompleted(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="SagaCompleted",
            saga_id=saga.id,
            booking_id=saga.booking_id,
        )
        await self.event_publisher.publish(event)
        
        logger.info(f"Saga {saga.id} completed successfully")
    
    async def compensate_saga(self, saga: PaymentSaga, reason: str) -> None:
        """
        Compensate saga (rollback)
        
        Executes compensation in reverse order of completed steps.
        
        Args:
            saga: Saga to compensate
            reason: Reason for compensation
        """
        logger.warning(f"Compensating saga {saga.id}: {reason}")
        
        # Transition to compensating
        saga.transition_to(SagaState.COMPENSATING)
        await self.saga_repository.save(saga)
        
        # Publish event
        event = SagaCompensating(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="SagaCompensating",
            saga_id=saga.id,
            booking_id=saga.booking_id,
            reason=reason,
        )
        await self.event_publisher.publish(event)
        
        # Get completed steps (in reverse order)
        completed_steps = saga.get_completed_steps()
        completed_steps.reverse()
        
        # Compensate each completed step
        for step in completed_steps:
            try:
                logger.info(f"Compensating step {step.name}")
                await self._compensate_step(saga, step.name)
            except Exception as e:
                logger.error(
                    f"Compensation failed for step {step.name}: {e}"
                )
                # Continue with other compensations
        
        # Mark as compensated
        saga.transition_to(SagaState.COMPENSATED)
        await self.saga_repository.save(saga)
        
        # Publish event
        event = SagaCompensated(
            event_id=str(uuid4()),
            occurred_at=datetime.now(timezone.utc),
            event_type="SagaCompensated",
            saga_id=saga.id,
            booking_id=saga.booking_id,
        )
        await self.event_publisher.publish(event)
        
        # Send failure notification
        await self.notification_service.send_payment_failure(
            booking_id=saga.booking_id,
            reason=reason,
        )
        
        logger.info(f"Saga {saga.id} compensated successfully")
        return saga
    
    async def _compensate_step(self, saga: PaymentSaga, step_name: str) -> None:
        """
        Compensate a single step
        
        Args:
            saga: Saga being compensated
            step_name: Name of step to compensate
        """
        if step_name == "RESERVE_BOOKING":
            # Cancel booking
            await self.booking_service.cancel_booking(
                booking_id=saga.booking_id,
                reason="Payment failed",
            )
        elif step_name == "PROCESS_PAYMENT":
            if saga.payment_id:
                await self.payment_gateway.refund_payment(
                    payment_id=saga.payment_id,
                    amount=saga.amount,
                )
                logger.info(f"Payment {saga.payment_id} refunded successfully")
            else:
                logger.warning("Cannot refund: no payment_id stored in saga")
        elif step_name == "CONFIRM_BOOKING":
            # Cancel booking
            await self.booking_service.cancel_booking(
                booking_id=saga.booking_id,
                reason="Saga compensation",
            )
        # SEND_NOTIFICATION doesn't need compensation
    
    async def get_saga(self, saga_id: SagaId) -> Optional[PaymentSaga]:
        """
        Get saga by ID
        
        Args:
            saga_id: Saga identifier
            
        Returns:
            Saga if found
        """
        return await self.saga_repository.find_by_id(saga_id)
    
    async def get_saga_by_booking(
        self,
        booking_id: BookingId
    ) -> Optional[PaymentSaga]:
        """
        Get saga by booking ID
        
        Args:
            booking_id: Booking identifier
            
        Returns:
            Saga if found
        """
        return await self.saga_repository.find_by_booking_id(booking_id)

    async def list_sagas(
        self,
        limit: int = 100,
        last_key: Optional[str] = None
    ) -> tuple[List[PaymentSaga], Optional[str]]:
        """
        List all sagas with pagination
        
        Args:
            limit: Maximum number of sagas to return
            last_key: Pagination token
            
        Returns:
            Tuple of (sagas, next_page_token)
        """
        return await self.saga_repository.find_all(limit, last_key)
