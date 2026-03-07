"""
Email Templates

Predefined templates for different notification types.
"""

from typing import Dict, Any
from .value_objects import NotificationType, EmailSubject, EmailBody, TemplateData


class EmailTemplate:
    """Base class for email templates"""
    
    @staticmethod
    def render_subject(template_data: TemplateData) -> EmailSubject:
        """Render email subject with template data"""
        raise NotImplementedError
    
    @staticmethod
    def render_body(template_data: TemplateData) -> EmailBody:
        """Render email body with template data"""
        raise NotImplementedError


class BookingConfirmedTemplate(EmailTemplate):
    """Template for booking confirmation emails"""
    
    @staticmethod
    def render_subject(template_data: TemplateData) -> EmailSubject:
        return EmailSubject("Booking Confirmed - Event Management")
    
    @staticmethod
    def render_body(template_data: TemplateData) -> EmailBody:
        booking_id = template_data.get("bookingId", "N/A")
        event_name = template_data.get("eventName", "Event")
        ticket_quantity = template_data.get("ticketQuantity", 0)
        total_price = template_data.get("totalPrice", 0)
        
        body = f"""
Dear Customer,

Your booking has been confirmed!

Booking Details:
- Booking ID: {booking_id}
- Event: {event_name}
- Tickets: {ticket_quantity}
- Total: ${total_price:.2f}

Thank you for your purchase!

Best regards,
Event Management Team
"""
        return EmailBody(body.strip())


class BookingCancelledTemplate(EmailTemplate):
    """Template for booking cancellation emails"""
    
    @staticmethod
    def render_subject(template_data: TemplateData) -> EmailSubject:
        return EmailSubject("Booking Cancelled - Event Management")
    
    @staticmethod
    def render_body(template_data: TemplateData) -> EmailBody:
        booking_id = template_data.get("bookingId", "N/A")
        reason = template_data.get("reason", "No reason provided")
        
        body = f"""
Dear Customer,

Your booking has been cancelled.

Booking ID: {booking_id}
Reason: {reason}

If you have any questions, please contact our support team.

Best regards,
Event Management Team
"""
        return EmailBody(body.strip())


class PaymentProcessedTemplate(EmailTemplate):
    """Template for payment confirmation emails"""
    
    @staticmethod
    def render_subject(template_data: TemplateData) -> EmailSubject:
        return EmailSubject("Payment Processed - Event Management")
    
    @staticmethod
    def render_body(template_data: TemplateData) -> EmailBody:
        booking_id = template_data.get("bookingId", "N/A")
        amount = template_data.get("amount", 0)
        currency = template_data.get("currency", "USD")
        
        body = f"""
Dear Customer,

Your payment has been processed successfully!

Payment Details:
- Booking ID: {booking_id}
- Amount: {amount:.2f} {currency}
- Status: Completed

Your tickets will be sent to you shortly.

Best regards,
Event Management Team
"""
        return EmailBody(body.strip())


class PaymentFailedTemplate(EmailTemplate):
    """Template for payment failure emails"""
    
    @staticmethod
    def render_subject(template_data: TemplateData) -> EmailSubject:
        return EmailSubject("Payment Failed - Event Management")
    
    @staticmethod
    def render_body(template_data: TemplateData) -> EmailBody:
        booking_id = template_data.get("bookingId", "N/A")
        reason = template_data.get("reason", "Payment declined")
        
        body = f"""
Dear Customer,

Unfortunately, your payment could not be processed.

Booking ID: {booking_id}
Reason: {reason}

Please try again or contact your payment provider.

Best regards,
Event Management Team
"""
        return EmailBody(body.strip())


class EventPublishedTemplate(EmailTemplate):
    """Template for event published emails"""
    
    @staticmethod
    def render_subject(template_data: TemplateData) -> EmailSubject:
        event_name = template_data.get("eventName", "New Event")
        return EmailSubject(f"New Event: {event_name}")
    
    @staticmethod
    def render_body(template_data: TemplateData) -> EmailBody:
        event_name = template_data.get("eventName", "Event")
        event_date = template_data.get("eventDate", "TBD")
        venue = template_data.get("venue", "TBD")
        
        body = f"""
Dear Customer,

A new event has been published!

Event Details:
- Name: {event_name}
- Date: {event_date}
- Venue: {venue}

Book your tickets now!

Best regards,
Event Management Team
"""
        return EmailBody(body.strip())


class TemplateFactory:
    """Factory to get appropriate template for notification type"""
    
    _templates: Dict[NotificationType, type[EmailTemplate]] = {
        NotificationType.BOOKING_CONFIRMED: BookingConfirmedTemplate,
        NotificationType.BOOKING_CANCELLED: BookingCancelledTemplate,
        NotificationType.PAYMENT_PROCESSED: PaymentProcessedTemplate,
        NotificationType.PAYMENT_FAILED: PaymentFailedTemplate,
        NotificationType.EVENT_PUBLISHED: EventPublishedTemplate,
    }
    
    @classmethod
    def get_template(cls, notification_type: NotificationType) -> EmailTemplate:
        """
        Get template for notification type
        
        Args:
            notification_type: Type of notification
            
        Returns:
            EmailTemplate instance
            
        Raises:
            ValueError: If template not found for type
        """
        template_class = cls._templates.get(notification_type)
        if not template_class:
            raise ValueError(f"No template found for {notification_type}")
        
        return template_class()
