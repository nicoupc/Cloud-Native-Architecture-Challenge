"""Unit tests for NotificationProcessor"""

import json
import pytest
from unittest.mock import AsyncMock, Mock
from src.application.notification_processor import NotificationProcessor
from src.domain.value_objects import (
    NotificationType,
    EmailAddress,
    EmailSubject,
    EmailBody
)


@pytest.mark.asyncio
class TestNotificationProcessor:
    async def test_process_message_success(self):
        # Mock email provider
        email_provider = AsyncMock()
        email_provider.send_email.return_value = True
        
        processor = NotificationProcessor(email_provider)
        
        message_body = json.dumps({
            "type": "BOOKING_CONFIRMED",
            "email": "user@example.com",
            "bookingId": "123",
            "eventName": "Concert",
            "ticketQuantity": 2,
            "totalPrice": 100.0
        })
        
        result = await processor.process_message(message_body)
        
        assert result is True
        email_provider.send_email.assert_called_once()
    
    async def test_process_message_email_failure(self):
        # Mock email provider that fails
        email_provider = AsyncMock()
        email_provider.send_email.return_value = False
        
        processor = NotificationProcessor(email_provider)
        
        message_body = json.dumps({
            "type": "BOOKING_CONFIRMED",
            "email": "user@example.com",
            "bookingId": "123"
        })
        
        result = await processor.process_message(message_body)
        
        assert result is False
    
    async def test_process_message_invalid_message(self):
        email_provider = AsyncMock()
        processor = NotificationProcessor(email_provider)
        
        result = await processor.process_message("invalid json")
        
        assert result is False
        email_provider.send_email.assert_not_called()
