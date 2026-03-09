"""
Tests for MockPaymentGateway
"""

import pytest
from unittest.mock import patch

from src.infrastructure.gateway.mock_payment_gateway import MockPaymentGateway
from src.domain.ports import PaymentGatewayError
from src.domain.value_objects import BookingId, Amount


class TestMockPaymentGatewayProcessPayment:
    """Test MockPaymentGateway.process_payment"""

    async def test_should_process_payment_successfully(self):
        """Payment succeeds when random value < success_rate"""
        gateway = MockPaymentGateway(success_rate=0.8)
        booking_id = BookingId.from_string("booking-123")
        amount = Amount(value=100.0, currency="USD")

        with patch("src.infrastructure.gateway.mock_payment_gateway.random.random", return_value=0.5):
            result = await gateway.process_payment(booking_id, amount)

        assert result["status"] == "COMPLETED"
        assert result["booking_id"] == "booking-123"
        assert result["amount"] == 100.0
        assert result["currency"] == "USD"
        assert result["provider"] == "MOCK_GATEWAY"

    async def test_should_return_payment_id_in_result(self):
        """Result contains a non-empty payment_id"""
        gateway = MockPaymentGateway(success_rate=1.0)
        booking_id = BookingId.from_string("booking-456")
        amount = Amount(value=50.0)

        result = await gateway.process_payment(booking_id, amount)

        assert "payment_id" in result
        assert isinstance(result["payment_id"], str)
        assert len(result["payment_id"]) > 0

    async def test_should_store_processed_payment(self):
        """Processed payment is stored internally"""
        gateway = MockPaymentGateway(success_rate=1.0)
        booking_id = BookingId.from_string("booking-789")
        amount = Amount(value=200.0)

        result = await gateway.process_payment(booking_id, amount)
        payment_id = result["payment_id"]

        stored = gateway.get_payment(payment_id)
        assert stored is not None
        assert stored["payment_id"] == payment_id

    async def test_should_fail_payment_when_random_exceeds_success_rate(self):
        """Payment fails when random value >= success_rate"""
        gateway = MockPaymentGateway(success_rate=0.8)
        booking_id = BookingId.from_string("booking-fail")
        amount = Amount(value=100.0)

        with patch("src.infrastructure.gateway.mock_payment_gateway.random.random", return_value=0.9):
            with pytest.raises(PaymentGatewayError, match="Payment declined"):
                await gateway.process_payment(booking_id, amount)

    async def test_should_raise_payment_gateway_error_on_failure(self):
        """PaymentGatewayError is raised with zero success rate"""
        gateway = MockPaymentGateway(success_rate=0.0)
        booking_id = BookingId.from_string("booking-zero")
        amount = Amount(value=100.0)

        with pytest.raises(PaymentGatewayError):
            await gateway.process_payment(booking_id, amount)


class TestMockPaymentGatewayRefund:
    """Test MockPaymentGateway.refund_payment"""

    async def test_should_refund_payment_successfully(self):
        """Refund succeeds for a previously processed payment"""
        gateway = MockPaymentGateway(success_rate=1.0)
        booking_id = BookingId.from_string("booking-refund")
        amount = Amount(value=150.0, currency="USD")

        result = await gateway.process_payment(booking_id, amount)
        payment_id = result["payment_id"]

        refund_result = await gateway.refund_payment(payment_id, amount)

        assert refund_result["refund_id"] is not None
        assert refund_result["payment_id"] == payment_id
        assert refund_result["amount"] == 150.0
        assert refund_result["currency"] == "USD"
        assert refund_result["status"] == "COMPLETED"

    async def test_should_update_payment_status_to_refunded(self):
        """Original payment status is updated to REFUNDED"""
        gateway = MockPaymentGateway(success_rate=1.0)
        booking_id = BookingId.from_string("booking-status")
        amount = Amount(value=75.0)

        result = await gateway.process_payment(booking_id, amount)
        payment_id = result["payment_id"]

        await gateway.refund_payment(payment_id, amount)

        stored = gateway.get_payment(payment_id)
        assert stored["status"] == "REFUNDED"

    async def test_should_raise_error_for_unknown_payment_id(self):
        """Refund fails for a non-existent payment"""
        gateway = MockPaymentGateway()
        amount = Amount(value=50.0)

        with pytest.raises(PaymentGatewayError, match="not found"):
            await gateway.refund_payment("non-existent-id", amount)

    async def test_should_raise_error_when_refund_exceeds_amount(self):
        """Refund fails when amount exceeds original payment"""
        gateway = MockPaymentGateway(success_rate=1.0)
        booking_id = BookingId.from_string("booking-exceed")
        original_amount = Amount(value=50.0)
        refund_amount = Amount(value=100.0)

        result = await gateway.process_payment(booking_id, original_amount)
        payment_id = result["payment_id"]

        with pytest.raises(PaymentGatewayError, match="exceeds"):
            await gateway.refund_payment(payment_id, refund_amount)


class TestMockPaymentGatewayGetPayment:
    """Test MockPaymentGateway.get_payment"""

    async def test_should_return_none_for_unknown_payment(self):
        """get_payment returns None for non-existent payment"""
        gateway = MockPaymentGateway()
        assert gateway.get_payment("unknown-id") is None
