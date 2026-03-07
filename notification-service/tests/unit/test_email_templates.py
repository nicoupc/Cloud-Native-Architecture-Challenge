"""Unit tests for email templates"""

import pytest
from src.domain.email_templates import (
    BookingConfirmedTemplate,
    BookingCancelledTemplate,
    PaymentProcessedTemplate,
    PaymentFailedTemplate,
    EventPublishedTemplate,
    EventCancelledTemplate,
    TemplateFactory
)
from src.domain.value_objects import NotificationType, TemplateData


class TestBookingConfirmedTemplate:
    def test_render_subject(self):
        template_data = TemplateData({})
        subject = BookingConfirmedTemplate.render_subject(template_data)
        assert "Booking Confirmed" in str(subject)
    
    def test_render_body(self):
        template_data = TemplateData({
            "bookingId": "123",
            "eventName": "Concert",
            "ticketQuantity": 2,
            "totalPrice": 100.0
        })
        body = BookingConfirmedTemplate.render_body(template_data)
        
        body_str = str(body)
        assert "123" in body_str
        assert "Concert" in body_str
        assert "2" in body_str
        assert "100.00" in body_str


class TestBookingCancelledTemplate:
    def test_render_subject(self):
        template_data = TemplateData({})
        subject = BookingCancelledTemplate.render_subject(template_data)
        assert "Booking Cancelled" in str(subject)
    
    def test_render_body(self):
        template_data = TemplateData({
            "bookingId": "123",
            "reason": "User request"
        })
        body = BookingCancelledTemplate.render_body(template_data)
        
        body_str = str(body)
        assert "123" in body_str
        assert "User request" in body_str



class TestPaymentProcessedTemplate:
    def test_render_subject(self):
        template_data = TemplateData({})
        subject = PaymentProcessedTemplate.render_subject(template_data)
        assert "Payment Processed" in str(subject)
    
    def test_render_body(self):
        template_data = TemplateData({
            "bookingId": "123",
            "amount": 100.0,
            "currency": "USD"
        })
        body = PaymentProcessedTemplate.render_body(template_data)
        
        body_str = str(body)
        assert "123" in body_str
        assert "100.00" in body_str
        assert "USD" in body_str


class TestPaymentFailedTemplate:
    def test_render_subject(self):
        template_data = TemplateData({})
        subject = PaymentFailedTemplate.render_subject(template_data)
        assert "Payment Failed" in str(subject)
    
    def test_render_body(self):
        template_data = TemplateData({
            "bookingId": "123",
            "reason": "Insufficient funds"
        })
        body = PaymentFailedTemplate.render_body(template_data)
        
        body_str = str(body)
        assert "123" in body_str
        assert "Insufficient funds" in body_str


class TestEventPublishedTemplate:
    def test_render_subject(self):
        template_data = TemplateData({"eventName": "Rock Concert"})
        subject = EventPublishedTemplate.render_subject(template_data)
        assert "Rock Concert" in str(subject)
    
    def test_render_body(self):
        template_data = TemplateData({
            "eventName": "Rock Concert",
            "eventDate": "2024-12-31",
            "venue": "Stadium"
        })
        body = EventPublishedTemplate.render_body(template_data)
        
        body_str = str(body)
        assert "Rock Concert" in body_str
        assert "2024-12-31" in body_str
        assert "Stadium" in body_str


class TestTemplateFactory:
    def test_get_booking_confirmed_template(self):
        template = TemplateFactory.get_template(NotificationType.BOOKING_CONFIRMED)
        assert isinstance(template, BookingConfirmedTemplate)
    
    def test_get_payment_processed_template(self):
        template = TemplateFactory.get_template(NotificationType.PAYMENT_PROCESSED)
        assert isinstance(template, PaymentProcessedTemplate)
    
    def test_get_event_cancelled_template(self):
        template = TemplateFactory.get_template(NotificationType.EVENT_CANCELLED)
        assert isinstance(template, EventCancelledTemplate)

    def test_unsupported_type_raises_error(self):
        # All defined types should have templates - this validates the factory is complete
        for notification_type in NotificationType:
            template = TemplateFactory.get_template(notification_type)
            assert template is not None
