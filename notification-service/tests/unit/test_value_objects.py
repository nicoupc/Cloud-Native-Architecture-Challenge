"""Unit tests for value objects"""

import pytest
from src.domain.value_objects import (
    NotificationId,
    NotificationType,
    NotificationStatus,
    EmailAddress,
    EmailSubject,
    EmailBody,
    TemplateData
)


class TestNotificationId:
    def test_create_with_value(self):
        notification_id = NotificationId("123")
        assert notification_id.value == "123"
    
    def test_generate_creates_unique_id(self):
        id1 = NotificationId.generate()
        id2 = NotificationId.generate()
        assert id1.value != id2.value
    
    def test_empty_value_raises_error(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            NotificationId("")
    
    def test_str_representation(self):
        notification_id = NotificationId("123")
        assert str(notification_id) == "123"


class TestEmailAddress:
    def test_valid_email(self):
        email = EmailAddress("user@example.com")
        assert email.value == "user@example.com"
    
    def test_invalid_email_without_at(self):
        with pytest.raises(ValueError, match="Invalid email"):
            EmailAddress("invalid-email")

    def test_empty_email(self):
        with pytest.raises(ValueError, match="Invalid email"):
            EmailAddress("")
    
    def test_str_representation(self):
        email = EmailAddress("user@example.com")
        assert str(email) == "user@example.com"


class TestEmailSubject:
    def test_valid_subject(self):
        subject = EmailSubject("Test Subject")
        assert subject.value == "Test Subject"
    
    def test_empty_subject_raises_error(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            EmailSubject("")
    
    def test_subject_too_long_raises_error(self):
        long_subject = "a" * 201
        with pytest.raises(ValueError, match="too long"):
            EmailSubject(long_subject)
    
    def test_str_representation(self):
        subject = EmailSubject("Test")
        assert str(subject) == "Test"


class TestEmailBody:
    def test_valid_body(self):
        body = EmailBody("Test body content")
        assert body.value == "Test body content"
    
    def test_empty_body_raises_error(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            EmailBody("")
    
    def test_str_representation(self):
        body = EmailBody("Test")
        assert str(body) == "Test"


class TestTemplateData:
    def test_create_with_data(self):
        data = TemplateData({"key": "value"})
        assert data.data == {"key": "value"}
    
    def test_get_existing_key(self):
        data = TemplateData({"key": "value"})
        assert data.get("key") == "value"
    
    def test_get_missing_key_returns_default(self):
        data = TemplateData({})
        assert data.get("missing", "default") is "default"
    
    def test_dict_like_access(self):
        data = TemplateData({"key": "value"})
        assert data["key"] == "value"
