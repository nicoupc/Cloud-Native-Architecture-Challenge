"""Domain Layer - Pure business logic"""

from .value_objects import (
    NotificationId,
    NotificationType,
    NotificationStatus,
    EmailAddress,
    EmailSubject,
    EmailBody,
    TemplateData
)
from .notification import Notification
from .email_templates import (
    EmailTemplate,
    BookingConfirmedTemplate,
    BookingCancelledTemplate,
    PaymentProcessedTemplate,
    PaymentFailedTemplate,
    EventPublishedTemplate,
    TemplateFactory
)
from .events import DomainEvent, NotificationSent, NotificationFailed
from .ports import EmailProvider, NotificationRepository

__all__ = [
    "NotificationId",
    "NotificationType",
    "NotificationStatus",
    "EmailAddress",
    "EmailSubject",
    "EmailBody",
    "TemplateData",
    "Notification",
    "EmailTemplate",
    "BookingConfirmedTemplate",
    "BookingCancelledTemplate",
    "PaymentProcessedTemplate",
    "PaymentFailedTemplate",
    "EventPublishedTemplate",
    "TemplateFactory",
    "DomainEvent",
    "NotificationSent",
    "NotificationFailed",
    "EmailProvider",
    "NotificationRepository",
]
