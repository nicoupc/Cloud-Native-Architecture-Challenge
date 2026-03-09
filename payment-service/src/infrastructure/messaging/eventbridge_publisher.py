"""
EventBridge Publisher - Event publishing adapter

Implements EventPublisher port using AWS EventBridge.
Publishes domain events to event bus for other services.
"""

import os
import json
from typing import List
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

from ...domain.ports import EventPublisher
from ...domain.events import DomainEvent


class EventBridgePublisher(EventPublisher):
    """EventBridge implementation of EventPublisher"""
    
    def __init__(self, event_bus_name: str = None):
        """
        Initialize publisher
        
        Args:
            event_bus_name: EventBridge bus name (defaults to env var)
        """
        self.event_bus_name = event_bus_name or os.getenv(
            "EVENT_BUS_NAME",
            "event-management-bus"
        )
        
        # Configure EventBridge client for LocalStack
        endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        self.client = boto3.client(
            "events",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test")
        )
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a single domain event
        
        Args:
            event: Domain event to publish
            
        Raises:
            Exception: If publish fails
        """
        await self.publish_batch([event])
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple domain events
        
        Args:
            events: List of domain events to publish
            
        Raises:
            Exception: If publish fails
        """
        if not events:
            return
        
        try:
            entries = [
                self._create_event_entry(event)
                for event in events
            ]
            
            response = self.client.put_events(Entries=entries)
            
            # Check for failures
            if response.get("FailedEntryCount", 0) > 0:
                failed = [
                    entry for entry in response.get("Entries", [])
                    if "ErrorCode" in entry
                ]
                raise Exception(f"Failed to publish {len(failed)} events: {failed}")
                
        except ClientError as e:
            raise Exception(f"Failed to publish events: {e.response['Error']['Message']}")
    
    def _create_event_entry(self, event: DomainEvent) -> dict:
        """
        Create EventBridge entry from domain event
        
        Args:
            event: Domain event
            
        Returns:
            EventBridge entry dictionary
        """
        return {
            "Time": datetime.now(timezone.utc),
            "Source": "payment-service",
            "DetailType": event.event_type,
            "Detail": json.dumps(event.to_dict()),
            "EventBusName": self.event_bus_name
        }
