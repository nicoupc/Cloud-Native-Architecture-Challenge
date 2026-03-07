"""Unit tests for Notification aggregate"""

import pytest
from datetime import datetime
from src.domain.notification import Notification
from src.domain.value_objects import (
    NotificationId,
    NotificationType,
    NotificationStatus,
    EmailAddress,
    EmailSubject,
    EmailBody,
    TemplateData
)


class TestNotification:
    def test_create_notification(self):
        notification = Notification.create(
            notification_type=NotificationType.BOOKING_CONFIRMED,
            recipient=EmailAddress("user@example.com"),
            subject=EmailSubject("Test Subject"),
            body=EmailBody("Test Body")
        )
        
        assert notification.notification_type == NotificationType.BOOKING_CONFIRMED
        assert notification.recipient.value == "user@example.com"
        assert notification.status == NotificationStatus.PENDING
        assert notification.retry_count == 0
    
    def test_mark_as_sent(self):
        notification = Notification.create(
            notification_type=NotificationType.BOOKING_CONFIRMED,
            recipient=EmailAddress("user@example.com"),
            subject=EmailSubject("Test"),
            body=EmailBody("Test")
        )
        
        notification.mark_as_sent()
        
        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None
        assert notification.error_message is None

    def test_mark_as_sent_idempotent(self):
        notification = Notification.create(
            notification_type=NotificationType.BOOKING_CONFIRMED,
            recipient=EmailAddress("user@example.com"),
            subject=EmailSubject("Test"),
            body=EmailBody("Test")
        )
        
        notification.mark_as_sent()
        first_sent_at = notification.sent_at
        
        notification.mark_as_sent()
        
        assert notification.sent_at == first_sent_at
    
    def test_mark_as_failed(self):
        notification = Notification.create(
            notification_type=NotificationType.BOOKING_CONFIRMED,
            recipient=EmailAddress("user@example.com"),
            subject=EmailSubject("Test"),
            body=EmailBody("Test")
        )
        
        notification.mark_as_failed("Connection timeout")
        
        assert notification.status == NotificationStatus.FAILED
        assert notification.failed_at is not None
        assert notification.error_message == "Connection timeout"
        assert notification.retry_count == 1
    
    def test_can_retry_within_limit(self):
        notification = Notification.create(
            notification_type=NotificationType.BOOKING_CONFIRMED,
            recipient=EmailAddress("user@example.com"),
            subject=EmailSubject("Test"),
            body=EmailBody("Test")
        )
        
        assert notification.can_retry(max_retries=3) is True
        
        notification.mark_as_failed("Error 1")
        assert notification.can_retry(max_retries=3) is True
        
        notification.mark_as_failed("Error 2")
        assert notification.can_retry(max_retries=3) is True
        
        notification.mark_as_failed("Error 3")
        assert notification.can_retry(max_retries=3) is False
    
    def test_to_dict(self):
        notification = Notification.create(
            notification_type=NotificationType.BOOKING_CONFIRMED,
            recipient=EmailAddress("user@example.com"),
            subject=EmailSubject("Test Subject"),
            body=EmailBody("Test Body"),
            template_data=TemplateData({"key": "value"})
        )
        
        result = notification.to_dict()
        
        assert result["notification_type"] == "BOOKING_CONFIRMED"
        assert result["recipient"] == "user@example.com"
        assert result["subject"] == "Test Subject"
        assert result["body"] == "Test Body"
        assert result["status"] == "PENDING"
        assert result["template_data"] == {"key": "value"}
        assert result["retry_count"] == 0
