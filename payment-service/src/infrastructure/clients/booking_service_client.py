"""
Booking Service HTTP Client

Communicates with Booking Service via REST API.
"""

import os
import httpx
from typing import Dict

from ...domain.ports import BookingServiceClient, BookingServiceError
from ...domain.value_objects import BookingId


class HttpBookingServiceClient(BookingServiceClient):
    """HTTP client for Booking Service"""
    
    def __init__(self, base_url: str = None, timeout: float = 10.0):
        self.base_url = base_url or os.getenv(
            "BOOKING_SERVICE_URL",
            "http://localhost:3001"
        )
        self.timeout = timeout
    
    async def confirm_booking(self, booking_id: BookingId) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/bookings/{booking_id.value}/confirm"
                )
                
                if response.status_code == 404:
                    raise BookingServiceError(f"Booking {booking_id.value} not found")
                
                if response.status_code >= 400:
                    raise BookingServiceError(f"Failed to confirm booking: {response.text}")
                
                return response.json()
                
        except httpx.RequestError as e:
            raise BookingServiceError(f"Failed to connect to Booking Service: {str(e)}")
    
    async def cancel_booking(self, booking_id: BookingId, reason: str) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/bookings/{booking_id.value}/cancel",
                    json={"reason": reason}
                )
                
                if response.status_code == 404:
                    raise BookingServiceError(f"Booking {booking_id.value} not found")
                
                if response.status_code >= 400:
                    raise BookingServiceError(f"Failed to cancel booking: {response.text}")
                
                return response.json()
                
        except httpx.RequestError as e:
            raise BookingServiceError(f"Failed to connect to Booking Service: {str(e)}")
    
    async def get_booking(self, booking_id: BookingId) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/bookings/{booking_id.value}"
                )
                
                if response.status_code == 404:
                    raise BookingServiceError(f"Booking {booking_id.value} not found")
                
                if response.status_code >= 400:
                    raise BookingServiceError(f"Failed to get booking: {response.text}")
                
                return response.json()
                
        except httpx.RequestError as e:
            raise BookingServiceError(f"Failed to connect to Booking Service: {str(e)}")
