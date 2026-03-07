"""
Domain Events for Notification Service

Events that represent state changes in the notification domain.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from .value_objects import NotificationId, NotificationType


@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events"""
    event_id: str
    occurred_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        raise NotImplementedError


@dataclass(frozen=True)
class NotificationSent(DomainEvent):
    """Event raised when notification is successfully sent"""
    notification_id: NotificationId
    notification_type: NotificationType
    recipient: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": "NotificationSent",
            "event_id": self.event_id,
            "occurred_at": self.occurred_at.isoformat(),
            "notification_id": str(self.notification_id),
            "notification_type": self.notification_type.value,
            "recipient": self.recipient
        }


@dataclass(frozen=True)
class NotificationFailed(DomainEvent):
    """Event raised when notification fails to send"""
    notification_id: NotificationId
    notification_type: NotificationType
    recipient: str
    error_message: str
    retry_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": "NotificationFailed",
            "event_id": self.event_id,
            "occurred_at": self.occurred_at.isoformat(),
            "notification_id": str(self.notification_id),
            "notification_type": self.notification_type.value,
            "recipient": self.recipient,
            "error_message": self.error_message,
            "retry_count": self.retry_count
        }
