"""
Tests for infrastructure clients (BookingServiceClient, NotificationServiceClient)
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, ANY

import httpx

from src.infrastructure.clients.booking_service_client import HttpBookingServiceClient
from src.infrastructure.clients.notification_service_client import EventBridgeNotificationClient
from src.domain.ports import BookingServiceError
from src.domain.value_objects import BookingId, Amount


class TestHttpBookingServiceClientConfirm:
    """Test HttpBookingServiceClient.confirm_booking"""

    async def test_should_confirm_booking_via_http(self):
        """Successful booking confirmation returns response JSON"""
        client = HttpBookingServiceClient(base_url="http://test-host:3001")
        booking_id = BookingId.from_string("booking-confirm")

        mock_response = httpx.Response(
            status_code=200,
            json={"id": "booking-confirm", "status": "CONFIRMED"},
            request=httpx.Request("POST", "http://test-host:3001/api/v1/bookings/booking-confirm/confirm"),
        )

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.post.return_value = mock_response
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await client.confirm_booking(booking_id)

        assert result["status"] == "CONFIRMED"
        mock_ctx.post.assert_called_once()

    async def test_should_raise_error_for_404(self):
        """BookingServiceError is raised when booking is not found"""
        client = HttpBookingServiceClient(base_url="http://test-host:3001")
        booking_id = BookingId.from_string("booking-missing")

        mock_response = httpx.Response(
            status_code=404,
            text="Not found",
            request=httpx.Request("POST", "http://test-host:3001/api/v1/bookings/booking-missing/confirm"),
        )

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.post.return_value = mock_response
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(BookingServiceError, match="not found"):
                await client.confirm_booking(booking_id)

    async def test_should_raise_error_for_server_error(self):
        """BookingServiceError is raised for HTTP 500"""
        client = HttpBookingServiceClient(base_url="http://test-host:3001")
        booking_id = BookingId.from_string("booking-500")

        mock_response = httpx.Response(
            status_code=500,
            text="Internal server error",
            request=httpx.Request("POST", "http://test-host:3001/api/v1/bookings/booking-500/confirm"),
        )

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.post.return_value = mock_response
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(BookingServiceError, match="Failed to confirm"):
                await client.confirm_booking(booking_id)

    async def test_should_handle_connection_error(self):
        """BookingServiceError is raised when connection fails"""
        client = HttpBookingServiceClient(base_url="http://unreachable:3001")
        booking_id = BookingId.from_string("booking-conn")

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.post.side_effect = httpx.RequestError("Connection refused")
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(BookingServiceError, match="Failed to connect"):
                await client.confirm_booking(booking_id)


class TestHttpBookingServiceClientCancel:
    """Test HttpBookingServiceClient.cancel_booking"""

    async def test_should_cancel_booking_via_http(self):
        """Successful booking cancellation returns response JSON"""
        client = HttpBookingServiceClient(base_url="http://test-host:3001")
        booking_id = BookingId.from_string("booking-cancel")

        mock_response = httpx.Response(
            status_code=200,
            json={"id": "booking-cancel", "status": "CANCELLED"},
            request=httpx.Request("POST", "http://test-host:3001/api/v1/bookings/booking-cancel/cancel"),
        )

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.post.return_value = mock_response
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await client.cancel_booking(booking_id, "Payment failed")

        assert result["status"] == "CANCELLED"

    async def test_should_raise_error_for_cancel_404(self):
        """BookingServiceError on 404 during cancel"""
        client = HttpBookingServiceClient(base_url="http://test-host:3001")
        booking_id = BookingId.from_string("booking-cancel-404")

        mock_response = httpx.Response(
            status_code=404,
            text="Not found",
            request=httpx.Request("POST", "http://test-host:3001/api/v1/bookings/booking-cancel-404/cancel"),
        )

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.post.return_value = mock_response
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(BookingServiceError, match="not found"):
                await client.cancel_booking(booking_id, "test reason")

    async def test_should_handle_cancel_connection_error(self):
        """BookingServiceError on connection failure during cancel"""
        client = HttpBookingServiceClient(base_url="http://unreachable:3001")
        booking_id = BookingId.from_string("booking-cancel-conn")

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.post.side_effect = httpx.RequestError("Connection refused")
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(BookingServiceError, match="Failed to connect"):
                await client.cancel_booking(booking_id, "reason")


class TestHttpBookingServiceClientGetBooking:
    """Test HttpBookingServiceClient.get_booking"""

    async def test_should_get_booking_via_http(self):
        """Successful get_booking returns response JSON"""
        client = HttpBookingServiceClient(base_url="http://test-host:3001")
        booking_id = BookingId.from_string("booking-get")

        mock_response = httpx.Response(
            status_code=200,
            json={"id": "booking-get", "status": "PENDING"},
            request=httpx.Request("GET", "http://test-host:3001/api/v1/bookings/booking-get"),
        )

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.get.return_value = mock_response
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await client.get_booking(booking_id)

        assert result["id"] == "booking-get"

    async def test_should_raise_error_for_get_404(self):
        """BookingServiceError on 404 during get_booking"""
        client = HttpBookingServiceClient(base_url="http://test-host:3001")
        booking_id = BookingId.from_string("booking-get-missing")

        mock_response = httpx.Response(
            status_code=404,
            text="Not found",
            request=httpx.Request("GET", "http://test-host:3001/api/v1/bookings/booking-get-missing"),
        )

        with patch("src.infrastructure.clients.booking_service_client.httpx.AsyncClient") as MockClient:
            mock_ctx = AsyncMock()
            mock_ctx.get.return_value = mock_response
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(BookingServiceError, match="not found"):
                await client.get_booking(booking_id)


class TestEventBridgeNotificationClientConfirmation:
    """Test EventBridgeNotificationClient.send_payment_confirmation"""

    async def test_should_send_payment_confirmation(self):
        """Payment confirmation event is published to EventBridge"""
        with patch("src.infrastructure.clients.notification_service_client.boto3.client") as mock_boto:
            mock_events = MagicMock()
            mock_boto.return_value = mock_events

            client = EventBridgeNotificationClient(event_bus_name="test-bus")
            booking_id = BookingId.from_string("booking-notify")
            amount = Amount(value=99.99, currency="USD")

            await client.send_payment_confirmation(booking_id, amount)

            mock_events.put_events.assert_called_once()
            call_args = mock_events.put_events.call_args
            entries = call_args[1]["Entries"] if "Entries" in call_args[1] else call_args[0][0]
            entry = entries[0]
            assert entry["Source"] == "payment-service"
            assert entry["DetailType"] == "PaymentConfirmed"
            assert entry["EventBusName"] == "test-bus"

            detail = json.loads(entry["Detail"])
            assert detail["bookingId"] == "booking-notify"
            assert detail["amount"] == 99.99
            assert detail["status"] == "CONFIRMED"


class TestEventBridgeNotificationClientFailure:
    """Test EventBridgeNotificationClient.send_payment_failure"""

    async def test_should_send_payment_failure(self):
        """Payment failure event is published to EventBridge"""
        with patch("src.infrastructure.clients.notification_service_client.boto3.client") as mock_boto:
            mock_events = MagicMock()
            mock_boto.return_value = mock_events

            client = EventBridgeNotificationClient(event_bus_name="test-bus")
            booking_id = BookingId.from_string("booking-fail-notify")

            await client.send_payment_failure(booking_id, "Card declined")

            mock_events.put_events.assert_called_once()
            call_args = mock_events.put_events.call_args
            entries = call_args[1]["Entries"] if "Entries" in call_args[1] else call_args[0][0]
            entry = entries[0]
            assert entry["DetailType"] == "PaymentFailed"

            detail = json.loads(entry["Detail"])
            assert detail["bookingId"] == "booking-fail-notify"
            assert detail["reason"] == "Card declined"
            assert detail["status"] == "FAILED"
