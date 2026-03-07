"""
Tests for Value Objects
"""

import pytest
from datetime import datetime
from src.domain.value_objects import SagaId, BookingId, Amount, SagaStep


class TestSagaId:
    """Test SagaId value object"""
    
    def test_generate_creates_valid_id(self):
        """Test that generate() creates a valid UUID"""
        saga_id = SagaId.generate()
        assert saga_id.value
        assert len(saga_id.value) == 36  # UUID format
        assert "-" in saga_id.value
    
    def test_from_string_valid_uuid(self):
        """Test creating SagaId from valid UUID string"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        saga_id = SagaId.from_string(uuid_str)
        assert saga_id.value == uuid_str
    
    def test_from_string_invalid_uuid(self):
        """Test that invalid UUID raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            SagaId.from_string("not-a-uuid")
        assert "Invalid saga ID format" in str(exc_info.value)
    
    def test_saga_id_immutable(self):
        """Test that SagaId is immutable"""
        saga_id = SagaId.generate()
        with pytest.raises(Exception):  # FrozenInstanceError
            saga_id.value = "new-value"  # type: ignore
    
    def test_str_representation(self):
        """Test string representation"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        saga_id = SagaId.from_string(uuid_str)
        assert str(saga_id) == uuid_str


class TestBookingId:
    """Test BookingId value object"""
    
    def test_from_string_valid(self):
        """Test creating BookingId from valid string"""
        booking_id = BookingId.from_string("booking-123")
        assert booking_id.value == "booking-123"
    
    def test_from_string_strips_whitespace(self):
        """Test that whitespace is stripped"""
        booking_id = BookingId.from_string("  booking-123  ")
        assert booking_id.value == "booking-123"
    
    def test_from_string_empty_raises_error(self):
        """Test that empty string raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            BookingId.from_string("")
        assert "cannot be empty" in str(exc_info.value)
    
    def test_from_string_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises ValueError"""
        with pytest.raises(ValueError):
            BookingId.from_string("   ")


class TestAmount:
    """Test Amount value object"""
    
    def test_create_valid_amount(self):
        """Test creating valid amount"""
        amount = Amount(value=100.50, currency="USD")
        assert amount.value == 100.50
        assert amount.currency == "USD"
    
    def test_default_currency_is_usd(self):
        """Test that default currency is USD"""
        amount = Amount(value=50.0)
        assert amount.currency == "USD"
    
    def test_negative_amount_raises_error(self):
        """Test that negative amount raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            Amount(value=-10.0)
        assert "cannot be negative" in str(exc_info.value)
    
    def test_invalid_currency_code_raises_error(self):
        """Test that invalid currency code raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            Amount(value=100.0, currency="US")  # Should be 3 letters
        assert "3-letter code" in str(exc_info.value)
    
    def test_str_representation(self):
        """Test string representation"""
        amount = Amount(value=123.45, currency="USD")
        assert str(amount) == "123.45 USD"
    
    def test_amount_immutable(self):
        """Test that Amount is immutable"""
        amount = Amount(value=100.0)
        with pytest.raises(Exception):  # FrozenInstanceError
            amount.value = 200.0  # type: ignore


class TestSagaStep:
    """Test SagaStep value object"""
    
    def test_create_pending_step(self):
        """Test creating a pending step"""
        step = SagaStep.create_pending("RESERVE_BOOKING")
        assert step.name == "RESERVE_BOOKING"
        assert step.status == "PENDING"
        assert step.started_at is None
        assert step.completed_at is None
        assert step.retry_count == 0
    
    def test_mark_started(self):
        """Test marking step as started"""
        step = SagaStep.create_pending("PROCESS_PAYMENT")
        started_step = step.mark_started()
        
        assert started_step.started_at is not None
        assert isinstance(started_step.started_at, datetime)
        assert started_step.status == "PENDING"  # Status doesn't change
    
    def test_mark_completed(self):
        """Test marking step as completed"""
        step = SagaStep.create_pending("CONFIRM_BOOKING")
        completed_step = step.mark_completed()
        
        assert completed_step.status == "COMPLETED"
        assert completed_step.completed_at is not None
        assert completed_step.error_message is None
    
    def test_mark_failed(self):
        """Test marking step as failed"""
        step = SagaStep.create_pending("PROCESS_PAYMENT")
        failed_step = step.mark_failed("Payment gateway timeout")
        
        assert failed_step.status == "FAILED"
        assert failed_step.error_message == "Payment gateway timeout"
        assert failed_step.completed_at is not None
    
    def test_increment_retry(self):
        """Test incrementing retry count"""
        step = SagaStep.create_pending("RESERVE_BOOKING")
        assert step.retry_count == 0
        
        retried_step = step.increment_retry()
        assert retried_step.retry_count == 1
        
        retried_again = retried_step.increment_retry()
        assert retried_again.retry_count == 2
    
    def test_invalid_status_raises_error(self):
        """Test that invalid status raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            SagaStep(
                name="TEST",
                status="INVALID_STATUS",
            )
        assert "Invalid step status" in str(exc_info.value)
    
    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            SagaStep(name="", status="PENDING")
        assert "cannot be empty" in str(exc_info.value)
