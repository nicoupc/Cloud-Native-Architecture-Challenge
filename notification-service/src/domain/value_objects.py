"""
Value Objects for Notification Domain

Immutable objects that represent domain concepts.
"""

from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4
from typing import Dict, Any


class NotificationType(Enum):
    """Types of notifications supported"""
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED"
    BOOKING_CANCELLED = "BOOKING_CANCELLED"
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    EVENT_PUBLISHED = "EVENT_PUBLISHED"
    EVENT_CANCELLED = "EVENT_CANCELLED"


class NotificationStatus(Enum):
    """Status of notification delivery"""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


@dataclass(frozen=True)
class NotificationId:
    """Notification unique identifier"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("NotificationId cannot be empty")
    
    @staticmethod
    def generate() -> "NotificationId":
        """Generate a new notification ID"""
        return NotificationId(str(uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EmailAddress:
    """Email address value object"""
    value: str
    
    def __post_init__(self):
        if not self.value or "@" not in self.value:
            raise ValueError(f"Invalid email address: {self.value}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EmailSubject:
    """Email subject value object"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Email subject cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Email subject too long (max 200 chars)")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EmailBody:
    """Email body value object"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Email body cannot be empty")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TemplateData:
    """Data for email template rendering"""
    data: Dict[str, Any]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from template data"""
        return self.data.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access"""
        return self.data[key]
