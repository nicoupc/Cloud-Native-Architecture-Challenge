"""
Notification Processor

Orchestrates notification processing workflow.
"""

import logging
from typing import Optional
from uuid import uuid4
from datetime import datetime, timezone

from ..domain import (
    Notification,
    NotificationType,
    EmailProvider,
    NotificationSent,
    NotificationFailed
)
from .message_handler import MessageHandler

logger = logging.getLogger(__name__)


class NotificationProcessor:
    """
    Processes notifications from SQS messages
    
    Orchestrates the workflow: parse → create → send → publish event
    """
    
    def __init__(self, email_provider: EmailProvider):
        """
        Initialize processor
        
        Args:
            email_provider: Email sending implementation
        """
        self.email_provider = email_provider
        self.message_handler = MessageHandler()
    
    async def process_message(self, message_body: str) -> bool:
        """
        Process a single SQS message
        
        Args:
            message_body: Raw message body from SQS
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Parse message
            parsed_data = self.message_handler.parse_message(message_body)
            if not parsed_data:
                logger.error("Failed to parse message")
                return False

            
            # Create notification data
            notification_data = self.message_handler.create_notification_data(
                notification_type=parsed_data["notification_type"],
                recipient=parsed_data["recipient"],
                template_data=parsed_data["template_data"]
            )
            
            if not notification_data:
                logger.error("Failed to create notification data")
                return False
            
            # Create notification aggregate
            notification = Notification.create(
                notification_type=notification_data["notification_type"],
                recipient=notification_data["recipient"],
                subject=notification_data["subject"],
                body=notification_data["body"],
                template_data=notification_data["template_data"]
            )
            
            # Send email
            success = await self.send_notification(notification)
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    async def send_notification(self, notification: Notification) -> bool:
        """
        Send notification via email provider
        
        Args:
            notification: Notification to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending notification {notification.notification_id}")
            
            # Send email
            success = await self.email_provider.send_email(
                recipient=notification.recipient,
                subject=notification.subject,
                body=notification.body
            )
            
            if success:
                notification.mark_as_sent()
                logger.info(f"Notification {notification.notification_id} sent successfully")
                
                # Create domain event
                event = NotificationSent(
                    event_id=str(uuid4()),
                    occurred_at=datetime.now(timezone.utc),
                    notification_id=notification.notification_id,
                    notification_type=notification.notification_type,
                    recipient=str(notification.recipient)
                )
                
                return True
            else:
                error_msg = "Email provider returned failure"
                notification.mark_as_failed(error_msg)
                logger.error(f"Failed to send notification {notification.notification_id}")
                
                # Create domain event
                event = NotificationFailed(
                    event_id=str(uuid4()),
                    occurred_at=datetime.now(timezone.utc),
                    notification_id=notification.notification_id,
                    notification_type=notification.notification_type,
                    recipient=str(notification.recipient),
                    error_message=error_msg,
                    retry_count=notification.retry_count
                )
                
                return False
                
        except Exception as e:
            error_msg = f"Exception during send: {str(e)}"
            notification.mark_as_failed(error_msg)
            logger.error(f"Error sending notification: {e}")
            return False
