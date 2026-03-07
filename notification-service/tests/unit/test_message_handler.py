"""Unit tests for MessageHandler"""

import json
import pytest
from src.application.message_handler import MessageHandler
from src.domain.value_objects import NotificationType


class TestMessageHandler:
    def test_parse_direct_message(self):
        message_body = json.dumps({
            "type": "BOOKING_CONFIRMED",
            "email": "user@example.com",
            "bookingId": "123"
        })
        
        result = MessageHandler.parse_message(message_body)
        
        assert result is not None
        assert result["notification_type"] == NotificationType.BOOKING_CONFIRMED
        assert result["recipient"] == "user@example.com"
    
    def test_parse_eventbridge_event(self):
        message_body = json.dumps({
            "detail-type": "BookingConfirmed",
            "detail": {
                "userEmail": "user@example.com",
                "bookingId": "123"
            }
        })
        
        result = MessageHandler.parse_message(message_body)
        
        assert result is not None
        assert result["notification_type"] == NotificationType.BOOKING_CONFIRMED
        assert result["recipient"] == "user@example.com"
    
    def test_parse_invalid_json(self):
        result = MessageHandler.parse_message("invalid json")
        assert result is None
    
    def test_parse_unknown_type(self):
        message_body = json.dumps({
            "type": "UNKNOWN_TYPE",
            "email": "user@example.com"
        })
        
        result = MessageHandler.parse_message(message_body)
        assert result is None
    
    def test_create_notification_data(self):
        result = MessageHandler.create_notification_data(
            notification_type=NotificationType.BOOKING_CONFIRMED,
            recipient="user@example.com",
            template_data={"bookingId": "123"}
        )
        
        assert result is not None
        assert result["notification_type"] == NotificationType.BOOKING_CONFIRMED
        assert str(result["recipient"]) == "user@example.com"
        assert result["subject"] is not None
        assert result["body"] is not None
