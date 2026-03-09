"""
Notification Aggregate Root

Represents a notification to be sent to a user.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from .value_objects import (
    NotificationId,
    NotificationType,
    NotificationStatus,
    EmailAddress,
    EmailSubject,
    EmailBody,
    TemplateData
)


class Notification:
    """
    Notification Aggregate Root
    
    Represents a notification that needs to be sent via email.
    """
    
    def __init__(
        self,
        notification_id: NotificationId,
        notification_type: NotificationType,
        recipient: EmailAddress,
        subject: EmailSubject,
        body: EmailBody,
        template_data: Optional[TemplateData] = None
    ):
        self._notification_id = notification_id
        self._notification_type = notification_type
        self._recipient = recipient
        self._subject = subject
        self._body = body
        self._template_data = template_data or TemplateData({})
        self._status = NotificationStatus.PENDING
        self._created_at = datetime.now(timezone.utc)
        self._sent_at: Optional[datetime] = None
        self._failed_at: Optional[datetime] = None
        self._error_message: Optional[str] = None
        self._retry_count = 0
    
    @property
    def notification_id(self) -> NotificationId:
        return self._notification_id
    
    @property
    def notification_type(self) -> NotificationType:
        return self._notification_type
    
    @property
    def recipient(self) -> EmailAddress:
        return self._recipient
    
    @property
    def subject(self) -> EmailSubject:
        return self._subject
    
    @property
    def body(self) -> EmailBody:
        return self._body
    
    @property
    def template_data(self) -> TemplateData:
        return self._template_data
    
    @property
    def status(self) -> NotificationStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def sent_at(self) -> Optional[datetime]:
        return self._sent_at
    
    @property
    def failed_at(self) -> Optional[datetime]:
        return self._failed_at
    
    @property
    def error_message(self) -> Optional[str]:
        return self._error_message
    
    @property
    def retry_count(self) -> int:
        return self._retry_count
    
    def mark_as_sent(self) -> None:
        """Mark notification as successfully sent"""
        if self._status == NotificationStatus.SENT:
            return  # Already sent, idempotent
        
        self._status = NotificationStatus.SENT
        self._sent_at = datetime.now(timezone.utc)
        self._error_message = None
    
    def mark_as_failed(self, error_message: str) -> None:
        """Mark notification as failed"""
        self._status = NotificationStatus.FAILED
        self._failed_at = datetime.now(timezone.utc)
        self._error_message = error_message
        self._retry_count += 1
    
    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if notification can be retried"""
        return self._retry_count < max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "notification_id": str(self._notification_id),
            "notification_type": self._notification_type.value,
            "recipient": str(self._recipient),
            "subject": str(self._subject),
            "body": str(self._body),
            "template_data": self._template_data.data,
            "status": self._status.value,
            "created_at": self._created_at.isoformat(),
            "sent_at": self._sent_at.isoformat() if self._sent_at else None,
            "failed_at": self._failed_at.isoformat() if self._failed_at else None,
            "error_message": self._error_message,
            "retry_count": self._retry_count
        }
    
    @staticmethod
    def create(
        notification_type: NotificationType,
        recipient: EmailAddress,
        subject: EmailSubject,
        body: EmailBody,
        template_data: Optional[TemplateData] = None
    ) -> "Notification":
        """
        Factory method to create a new notification
        
        Args:
            notification_type: Type of notification
            recipient: Email recipient
            subject: Email subject
            body: Email body
            template_data: Optional template data
            
        Returns:
            New Notification instance
        """
        notification_id = NotificationId.generate()
        
        return Notification(
            notification_id=notification_id,
            notification_type=notification_type,
            recipient=recipient,
            subject=subject,
            body=body,
            template_data=template_data
        )
    
    def __repr__(self) -> str:
        return (
            f"Notification(id={self._notification_id}, "
            f"type={self._notification_type.value}, "
            f"status={self._status.value})"
        )
