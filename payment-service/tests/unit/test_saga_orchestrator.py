"""
Tests for Saga Orchestrator

Uses mocks for all external dependencies (ports).
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.application.saga_orchestrator import SagaOrchestrator
from src.domain.payment_saga import PaymentSaga
from src.domain.saga_state import SagaState
from src.domain.value_objects import SagaId, BookingId, Amount
from src.domain.ports import PaymentGatewayError, BookingServiceError
from src.domain.exceptions import SagaNotFoundException


@pytest.fixture
def mock_saga_repository():
    """Mock saga repository"""
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_event_publisher():
    """Mock event publisher"""
    publisher = AsyncMock()
    return publisher


@pytest.fixture
def mock_payment_gateway():
    """Mock payment gateway"""
    gateway = AsyncMock()
    gateway.process_payment.return_value = {"payment_id": "payment-123"}
    return gateway


@pytest.fixture
def mock_booking_service():
    """Mock booking service client"""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_notification_service():
    """Mock notification service client"""
    service = AsyncMock()
    return service


@pytest.fixture
def orchestrator(
    mock_saga_repository,
    mock_event_publisher,
    mock_payment_gateway,
    mock_booking_service,
    mock_notification_service,
):
    """Create orchestrator with mocked dependencies"""
    return SagaOrchestrator(
        saga_repository=mock_saga_repository,
        event_publisher=mock_event_publisher,
        payment_gateway=mock_payment_gateway,
        booking_service=mock_booking_service,
        notification_service=mock_notification_service,
        max_retries=3,
    )


@pytest.fixture
def sample_saga():
    """Create a sample saga for testing"""
    return PaymentSaga.create(
        booking_id=BookingId.from_string("booking-123"),
        amount=Amount(value=100.0),
    )


class TestSagaOrchestratorStartSaga:
    """Test starting a new saga"""
    
    @pytest.mark.asyncio
    async def test_start_saga_creates_and_persists(
        self,
        orchestrator,
        mock_saga_repository,
        mock_event_publisher,
    ):
        """Test that start_saga creates and persists saga"""
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=100.0)
        
        # Mock repository to return the saga
        mock_saga_repository.save.return_value = PaymentSaga.create(
            booking_id=booking_id,
            amount=amount,
        )
        mock_saga_repository.find_by_id.return_value = None  # Stop execution
        
        saga = await orchestrator.start_saga(
            booking_id=booking_id,
            amount=amount,
        )
        
        # Verify saga was created
        assert saga.booking_id == booking_id
        assert saga.amount == amount
        assert saga.state == SagaState.STARTED
        
        # Verify saga was saved
        assert mock_saga_repository.save.called
        
        # Verify event was published
        assert mock_event_publisher.publish.called


class TestSagaOrchestratorExecuteSaga:
    """Test saga execution"""
    
    @pytest.mark.asyncio
    async def test_execute_saga_not_found_raises_exception(
        self,
        orchestrator,
        mock_saga_repository,
    ):
        """Test that executing non-existent saga raises exception"""
        saga_id = SagaId.generate()
        mock_saga_repository.find_by_id.return_value = None
        
        with pytest.raises(SagaNotFoundException):
            await orchestrator.execute_saga(saga_id)
    
    @pytest.mark.asyncio
    async def test_execute_saga_happy_path(
        self,
        orchestrator,
        mock_saga_repository,
        mock_payment_gateway,
        mock_booking_service,
        mock_notification_service,
        sample_saga,
    ):
        """Test successful saga execution (happy path)"""
        # Setup: saga exists and all steps succeed
        mock_saga_repository.find_by_id.return_value = sample_saga
        mock_saga_repository.save.return_value = sample_saga
        
        # Execute saga
        result = await orchestrator.execute_saga(sample_saga.id)
        
        # Verify all steps were executed
        assert mock_payment_gateway.process_payment.called
        assert mock_booking_service.confirm_booking.called
        assert mock_notification_service.send_payment_confirmation.called
        
        # Verify saga was saved multiple times (after each step)
        assert mock_saga_repository.save.call_count >= 4
    
    @pytest.mark.asyncio
    async def test_execute_saga_payment_fails_triggers_compensation(
        self,
        orchestrator,
        mock_saga_repository,
        mock_payment_gateway,
        mock_booking_service,
        sample_saga,
    ):
        """Test that payment failure triggers compensation"""
        # Setup: payment fails
        mock_saga_repository.find_by_id.return_value = sample_saga
        mock_saga_repository.save.return_value = sample_saga
        mock_payment_gateway.process_payment.side_effect = PaymentGatewayError(
            "Card declined"
        )
        
        # Execute saga
        await orchestrator.execute_saga(sample_saga.id)
        
        # Verify compensation was triggered
        assert mock_booking_service.cancel_booking.called
        
        # Verify failure notification was sent
        # (called in _compensate_saga)
        assert mock_saga_repository.save.called


class TestSagaOrchestratorStepExecution:
    """Test individual step execution"""
    
    @pytest.mark.asyncio
    async def test_reserve_booking_step(
        self,
        orchestrator,
        mock_saga_repository,
        mock_event_publisher,
        sample_saga,
    ):
        """Test reserve booking step"""
        await orchestrator._reserve_booking(sample_saga)
        
        # Verify state transition
        assert sample_saga.state == SagaState.BOOKING_RESERVED
        
        # Verify event was published
        assert mock_event_publisher.publish.called
    
    @pytest.mark.asyncio
    async def test_process_payment_step_success(
        self,
        orchestrator,
        mock_payment_gateway,
        mock_saga_repository,
        mock_event_publisher,
        sample_saga,
    ):
        """Test successful payment processing"""
        # Transition to correct state first
        sample_saga.transition_to(SagaState.BOOKING_RESERVED)
        
        await orchestrator._process_payment(sample_saga)
        
        # Verify payment gateway was called
        mock_payment_gateway.process_payment.assert_called_once_with(
            booking_id=sample_saga.booking_id,
            amount=sample_saga.amount,
        )
        
        # Verify state transition
        assert sample_saga.state == SagaState.PAYMENT_PROCESSED
    
    @pytest.mark.asyncio
    async def test_process_payment_step_failure(
        self,
        orchestrator,
        mock_payment_gateway,
        mock_event_publisher,
        sample_saga,
    ):
        """Test payment processing failure"""
        # Setup: payment fails
        sample_saga.transition_to(SagaState.BOOKING_RESERVED)
        mock_payment_gateway.process_payment.side_effect = PaymentGatewayError(
            "Insufficient funds"
        )
        
        # Should raise exception
        with pytest.raises(PaymentGatewayError):
            await orchestrator._process_payment(sample_saga)
        
        # Verify failure event was published
        assert mock_event_publisher.publish.called
    
    @pytest.mark.asyncio
    async def test_confirm_booking_step(
        self,
        orchestrator,
        mock_booking_service,
        mock_saga_repository,
        mock_event_publisher,
        sample_saga,
    ):
        """Test confirm booking step"""
        # Transition to correct state
        sample_saga.transition_to(SagaState.BOOKING_RESERVED)
        sample_saga.transition_to(SagaState.PAYMENT_PROCESSED)
        
        await orchestrator._confirm_booking(sample_saga)
        
        # Verify booking service was called
        mock_booking_service.confirm_booking.assert_called_once_with(
            sample_saga.booking_id
        )
        
        # Verify state transition
        assert sample_saga.state == SagaState.BOOKING_CONFIRMED


class TestSagaOrchestratorCompensation:
    """Test saga compensation (rollback)"""
    
    @pytest.mark.asyncio
    async def test_compensate_saga(
        self,
        orchestrator,
        mock_saga_repository,
        mock_event_publisher,
        mock_booking_service,
        mock_notification_service,
        sample_saga,
    ):
        """Test saga compensation"""
        # Setup: saga has completed some steps
        sample_saga.transition_to(SagaState.BOOKING_RESERVED)
        sample_saga.complete_current_step()  # RESERVE_BOOKING completed
        
        # Compensate
        await orchestrator._compensate_saga(sample_saga, "Payment failed")
        
        # Verify state transitions
        assert sample_saga.state == SagaState.COMPENSATED
        
        # Verify booking was cancelled
        assert mock_booking_service.cancel_booking.called
        
        # Verify failure notification was sent
        assert mock_notification_service.send_payment_failure.called
        
        # Verify events were published
        assert mock_event_publisher.publish.call_count >= 2  # Compensating + Compensated
    
    @pytest.mark.asyncio
    async def test_compensate_step_reserve_booking(
        self,
        orchestrator,
        mock_booking_service,
        sample_saga,
    ):
        """Test compensating RESERVE_BOOKING step"""
        await orchestrator._compensate_step(sample_saga, "RESERVE_BOOKING")
        
        # Verify booking was cancelled
        mock_booking_service.cancel_booking.assert_called_once_with(
            booking_id=sample_saga.booking_id,
            reason="Payment failed",
        )


class TestSagaOrchestratorQueries:
    """Test saga query methods"""
    
    @pytest.mark.asyncio
    async def test_get_saga(
        self,
        orchestrator,
        mock_saga_repository,
        sample_saga,
    ):
        """Test getting saga by ID"""
        mock_saga_repository.find_by_id.return_value = sample_saga
        
        result = await orchestrator.get_saga(sample_saga.id)
        
        assert result == sample_saga
        mock_saga_repository.find_by_id.assert_called_once_with(sample_saga.id)
    
    @pytest.mark.asyncio
    async def test_get_saga_by_booking(
        self,
        orchestrator,
        mock_saga_repository,
        sample_saga,
    ):
        """Test getting saga by booking ID"""
        mock_saga_repository.find_by_booking_id.return_value = sample_saga
        
        result = await orchestrator.get_saga_by_booking(sample_saga.booking_id)
        
        assert result == sample_saga
        mock_saga_repository.find_by_booking_id.assert_called_once_with(
            sample_saga.booking_id
        )
