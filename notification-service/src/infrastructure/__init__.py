"""Infrastructure Layer - External adapters"""

from .email.mock_email_provider import MockEmailProvider
from .queue.sqs_consumer import SQSConsumer

__all__ = ["MockEmailProvider", "SQSConsumer"]
