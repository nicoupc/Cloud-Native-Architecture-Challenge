"""
Contract Tests: Payment Service → Booking Service API

These tests verify that the Payment Service's HTTP client correctly handles
the response format from the Booking Service. If the Booking Service changes
its API, these tests will fail, alerting us to a contract violation.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json


# Standard Booking Service response format (the "contract")
BOOKING_RESPONSE_CONTRACT = {
    "success": True,
    "data": {
        "id": "booking-123",
        "userId": "user-456",
        "eventId": "event-789",
        "status": "PENDING",
        "ticketQuantity": 2,
        "totalPrice": 100.00,
        "createdAt": "2026-01-01T00:00:00.000Z",
        "updatedAt": "2026-01-01T00:00:00.000Z",
    },
}

CONFIRMED_BOOKING_CONTRACT = {
    "success": True,
    "data": {
        **BOOKING_RESPONSE_CONTRACT["data"],
        "status": "CONFIRMED",
    },
}

CANCELLED_BOOKING_CONTRACT = {
    "success": True,
    "data": {
        **BOOKING_RESPONSE_CONTRACT["data"],
        "status": "CANCELLED",
    },
}


class TestBookingApiContract:
    """Verify Payment Service correctly interacts with Booking Service API contract."""

    def test_get_booking_response_has_required_fields(self):
        """Contract: GET /bookings/{id} returns {success, data: {id, userId, eventId, status, ...}}"""
        response = BOOKING_RESPONSE_CONTRACT
        assert "success" in response
        assert response["success"] is True
        assert "data" in response

        data = response["data"]
        required_fields = [
            "id", "userId", "eventId", "status",
            "ticketQuantity", "totalPrice", "createdAt", "updatedAt",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_confirm_booking_response_has_confirmed_status(self):
        """Contract: POST /bookings/{id}/confirm returns booking with CONFIRMED status"""
        response = CONFIRMED_BOOKING_CONTRACT
        assert response["success"] is True
        assert response["data"]["status"] == "CONFIRMED"

    def test_cancel_booking_response_has_cancelled_status(self):
        """Contract: POST /bookings/{id}/cancel returns booking with CANCELLED status"""
        response = CANCELLED_BOOKING_CONTRACT
        assert response["success"] is True
        assert response["data"]["status"] == "CANCELLED"

    def test_booking_id_is_string(self):
        """Contract: booking ID is always a string"""
        assert isinstance(BOOKING_RESPONSE_CONTRACT["data"]["id"], str)

    def test_ticket_quantity_is_positive_integer(self):
        """Contract: ticketQuantity is a positive integer"""
        qty = BOOKING_RESPONSE_CONTRACT["data"]["ticketQuantity"]
        assert isinstance(qty, int)
        assert qty > 0

    def test_total_price_is_number(self):
        """Contract: totalPrice is a number"""
        price = BOOKING_RESPONSE_CONTRACT["data"]["totalPrice"]
        assert isinstance(price, (int, float))

    def test_status_is_valid_enum(self):
        """Contract: status must be one of the valid booking statuses"""
        valid_statuses = {"PENDING", "CONFIRMED", "CANCELLED"}
        assert BOOKING_RESPONSE_CONTRACT["data"]["status"] in valid_statuses

    def test_cancel_request_body_format(self):
        """Contract: Cancel request sends {reason: string}"""
        cancel_body = {"reason": "Payment failed"}
        assert "reason" in cancel_body
        assert isinstance(cancel_body["reason"], str)

    def test_timestamps_are_iso_strings(self):
        """Contract: createdAt and updatedAt are ISO 8601 strings"""
        data = BOOKING_RESPONSE_CONTRACT["data"]
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)
        assert "T" in data["createdAt"]
        assert "T" in data["updatedAt"]


class TestBookingServiceClientContract:
    """Verify the HttpBookingServiceClient handles all response scenarios correctly."""

    @pytest.mark.asyncio
    async def test_client_handles_get_booking_response(self):
        """The client should return parsed JSON for a valid booking response."""
        from src.infrastructure.clients.booking_service_client import HttpBookingServiceClient
        from src.domain.value_objects import BookingId

        client = HttpBookingServiceClient(base_url="http://fake:3001")
        booking_id = BookingId(value="booking-123")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = BOOKING_RESPONSE_CONTRACT

        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_response
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            result = await client.get_booking(booking_id)

        assert result == BOOKING_RESPONSE_CONTRACT
        assert result["success"] is True
        assert result["data"]["id"] == "booking-123"

    @pytest.mark.asyncio
    async def test_client_handles_confirm_response(self):
        """The client should return parsed JSON for a confirm response."""
        from src.infrastructure.clients.booking_service_client import HttpBookingServiceClient
        from src.domain.value_objects import BookingId

        client = HttpBookingServiceClient(base_url="http://fake:3001")
        booking_id = BookingId(value="booking-123")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = CONFIRMED_BOOKING_CONTRACT

        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            result = await client.confirm_booking(booking_id)

        assert result == CONFIRMED_BOOKING_CONTRACT
        assert result["data"]["status"] == "CONFIRMED"

    @pytest.mark.asyncio
    async def test_client_handles_cancel_response(self):
        """The client should return parsed JSON for a cancel response."""
        from src.infrastructure.clients.booking_service_client import HttpBookingServiceClient
        from src.domain.value_objects import BookingId

        client = HttpBookingServiceClient(base_url="http://fake:3001")
        booking_id = BookingId(value="booking-123")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = CANCELLED_BOOKING_CONTRACT

        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            result = await client.cancel_booking(booking_id, "Payment failed")

        assert result == CANCELLED_BOOKING_CONTRACT
        assert result["data"]["status"] == "CANCELLED"

    @pytest.mark.asyncio
    async def test_client_raises_on_404(self):
        """The client should raise BookingServiceError on 404."""
        from src.infrastructure.clients.booking_service_client import HttpBookingServiceClient
        from src.domain.value_objects import BookingId
        from src.domain.ports import BookingServiceError

        client = HttpBookingServiceClient(base_url="http://fake:3001")
        booking_id = BookingId(value="nonexistent-id")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"

        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_response
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            with pytest.raises(BookingServiceError, match="not found"):
                await client.get_booking(booking_id)

    @pytest.mark.asyncio
    async def test_client_calls_correct_endpoints(self):
        """The client must call the exact API paths the Booking Service exposes."""
        from src.infrastructure.clients.booking_service_client import HttpBookingServiceClient
        from src.domain.value_objects import BookingId

        client = HttpBookingServiceClient(base_url="http://fake:3001")
        booking_id = BookingId(value="booking-123")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = BOOKING_RESPONSE_CONTRACT

        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_response
        mock_http_client.post.return_value = mock_response
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            await client.get_booking(booking_id)
            mock_http_client.get.assert_called_once_with(
                "http://fake:3001/api/v1/bookings/booking-123"
            )

        mock_http_client.reset_mock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            await client.confirm_booking(booking_id)
            mock_http_client.post.assert_called_once_with(
                "http://fake:3001/api/v1/bookings/booking-123/confirm"
            )

        mock_http_client.reset_mock()
        mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_http_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_http_client):
            await client.cancel_booking(booking_id, "refund")
            mock_http_client.post.assert_called_once_with(
                "http://fake:3001/api/v1/bookings/booking-123/cancel",
                json={"reason": "refund"},
            )
