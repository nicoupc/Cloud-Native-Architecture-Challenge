"""
Notification Service Client

Sends notifications via EventBridge/SQS.
For this implementation, we publish events that Notification Service consumes.
"""

import os
import json
from datetime import datetime
import boto3

from ...domain.ports import NotificationServiceClient
from ...domain.value_objects import BookingId, Amount


class EventBridgeNotificationClient(NotificationServiceClient):
    """EventBridge-based notification client"""
    
    def __init__(self, event_bus_name: str = None):
        """
        Initialize client
        
        Args:
            event_bus_name: EventBridge bus name
        """
        self.event_bus_name = event_bus_name or os.getenv(
            "EVENT_BUS_NAME",
            "event-management-bus"
        )
        
        endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        self.client = boto3.client(
            "events",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test")
        )
    
    async def send_payment_confirmation(
        self,
        booking_id: BookingId,
        amount: Amount
    ) -> None:
        """
        Send payment confirmation notification
        
        Args:
            booking_id: Booking identifier
            amount: Payment amount
        """
        event = {
            "bookingId": booking_id.value,
            "amount": amount.value,
            "currency": amount.currency,
            "status": "CONFIRMED"
        }
        
        self.client.put_events(
            Entries=[{
                "Time": datetime.utcnow(),
                "Source": "payment-service",
                "DetailType": "PaymentConfirmed",
                "Detail": json.dumps(event),
                "EventBusName": self.event_bus_name
            }]
        )
    
    async def send_payment_failure(
        self,
        booking_id: BookingId,
        reason: str
    ) -> None:
        """
        Send payment failure notification
        
        Args:
            booking_id: Booking identifier
            reason: Failure reason
        """
        event = {
            "bookingId": booking_id.value,
            "reason": reason,
            "status": "FAILED"
        }
        
        self.client.put_events(
            Entries=[{
                "Time": datetime.utcnow(),
                "Source": "payment-service",
                "DetailType": "PaymentFailed",
                "Detail": json.dumps(event),
                "EventBusName": self.event_bus_name
            }]
        )
