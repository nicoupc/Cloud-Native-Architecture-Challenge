"""
Message Handler

Parses and validates messages from SQS.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..domain import (
    NotificationType,
    EmailAddress,
    EmailSubject,
    EmailBody,
    TemplateData,
    TemplateFactory
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Handles parsing and validation of SQS messages
    
    Supports EventBridge events and direct messages.
    """
    
    @staticmethod
    def parse_message(message_body: str) -> Optional[Dict[str, Any]]:
        """
        Parse SQS message body
        
        Args:
            message_body: Raw message body from SQS
            
        Returns:
            Parsed message data or None if invalid
        """
        try:
            data = json.loads(message_body)
            
            # Handle EventBridge event format
            if "detail-type" in data and "detail" in data:
                return MessageHandler._parse_eventbridge_event(data)
            
            # Handle direct message format
            return MessageHandler._parse_direct_message(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
            return None

    
    @staticmethod
    def _parse_eventbridge_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse EventBridge event format"""
        try:
            detail_type = event.get("detail-type", "")
            detail = event.get("detail", {})
            
            # Map EventBridge detail-type to NotificationType
            type_mapping = {
                "BookingConfirmed": NotificationType.BOOKING_CONFIRMED,
                "BookingCancelled": NotificationType.BOOKING_CANCELLED,
                "PaymentProcessed": NotificationType.PAYMENT_PROCESSED,
                "PaymentFailed": NotificationType.PAYMENT_FAILED,
                "EventPublished": NotificationType.EVENT_PUBLISHED,
                "EventCancelled": NotificationType.EVENT_CANCELLED,
            }
            
            notification_type = type_mapping.get(detail_type)
            if not notification_type:
                logger.warning(f"Unknown detail-type: {detail_type}")
                return None
            
            return {
                "notification_type": notification_type,
                "recipient": detail.get("userEmail"),
                "template_data": detail
            }
            
        except Exception as e:
            logger.error(f"Failed to parse EventBridge event: {e}")
            return None
    
    @staticmethod
    def _parse_direct_message(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse direct message format"""
        try:
            notification_type_str = data.get("type")
            if not notification_type_str:
                logger.error("Missing 'type' field in message")
                return None
            
            try:
                notification_type = NotificationType[notification_type_str]
            except KeyError:
                logger.error(f"Invalid notification type: {notification_type_str}")
                return None
            
            return {
                "notification_type": notification_type,
                "recipient": data.get("email"),
                "template_data": data
            }
            
        except Exception as e:
            logger.error(f"Failed to parse direct message: {e}")
            return None
    
    @staticmethod
    def create_notification_data(
        notification_type: NotificationType,
        recipient: str,
        template_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create notification data with rendered email content
        
        Args:
            notification_type: Type of notification
            recipient: Email recipient
            template_data: Data for template rendering
            
        Returns:
            Notification data or None if invalid
        """
        try:
            # Validate recipient
            email_address = EmailAddress(recipient)
            
            # Get template and render
            template = TemplateFactory.get_template(notification_type)
            template_data_obj = TemplateData(template_data)
            
            subject = template.render_subject(template_data_obj)
            body = template.render_body(template_data_obj)
            
            return {
                "notification_type": notification_type,
                "recipient": email_address,
                "subject": subject,
                "body": body,
                "template_data": template_data_obj
            }
            
        except Exception as e:
            logger.error(f"Failed to create notification data: {e}")
            return None
