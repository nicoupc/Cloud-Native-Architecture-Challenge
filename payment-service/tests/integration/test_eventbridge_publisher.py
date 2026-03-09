"""
EventBridge Publisher Integration Tests

Tests publishing real events to EventBridge via LocalStack.
Automatically skipped if LocalStack is not running.
"""

import pytest
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.infrastructure.messaging.eventbridge_publisher import EventBridgePublisher
from src.domain.events import SagaStarted
from src.domain.value_objects import SagaId, BookingId, Amount

LOCALSTACK_URL = "http://localhost:4566"
TEST_BUS_NAME = "payment-integration-test-bus"


def localstack_available():
    """Check if LocalStack is running and healthy."""
    try:
        import httpx
        r = httpx.get(f"{LOCALSTACK_URL}/_localstack/health", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not localstack_available(),
    reason="LocalStack not available",
)


@pytest.fixture(scope="module")
def eventbridge_client():
    """Create a real EventBridge client pointing to LocalStack."""
    return boto3.client(
        "events",
        endpoint_url=LOCALSTACK_URL,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture(scope="module")
def event_bus(eventbridge_client):
    """Create a test EventBridge bus. Clean up after tests."""
    try:
        eventbridge_client.create_event_bus(Name=TEST_BUS_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceAlreadyExistsException":
            raise

    yield TEST_BUS_NAME

    try:
        eventbridge_client.delete_event_bus(Name=TEST_BUS_NAME)
    except Exception:
        pass


@pytest.fixture
def publisher(event_bus):
    """Create an EventBridgePublisher pointing to the test bus."""
    os.environ["AWS_ENDPOINT_URL"] = LOCALSTACK_URL
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["EVENT_BUS_NAME"] = TEST_BUS_NAME
    return EventBridgePublisher(event_bus_name=TEST_BUS_NAME)


def create_test_event() -> SagaStarted:
    """Create a test SagaStarted domain event."""
    return SagaStarted(
        event_id=str(uuid4()),
        occurred_at=datetime.now(timezone.utc),
        event_type="SagaStarted",
        saga_id=SagaId.generate(),
        booking_id=BookingId("booking-eb-test-001"),
        amount=Amount(99.99, "USD"),
    )


class TestEventBridgePublisher:
    """Integration tests for EventBridgePublisher."""

    @pytest.mark.asyncio
    async def test_publish_single_event(self, publisher):
        """Test publishing a single domain event to EventBridge."""
        event = create_test_event()
        # Should not raise any exceptions
        await publisher.publish(event)

    @pytest.mark.asyncio
    async def test_publish_batch_events(self, publisher):
        """Test publishing a batch of domain events."""
        events = [create_test_event() for _ in range(3)]
        await publisher.publish_batch(events)

    @pytest.mark.asyncio
    async def test_publish_empty_batch(self, publisher):
        """Test that empty batch is handled gracefully."""
        await publisher.publish_batch([])

    @pytest.mark.asyncio
    async def test_publish_event_reaches_eventbridge(self, eventbridge_client, publisher, event_bus):
        """Test that published events are accepted by EventBridge."""
        event = create_test_event()
        # If this doesn't throw, EventBridge accepted the event
        await publisher.publish(event)

        # Verify the bus exists and is functional
        response = eventbridge_client.describe_event_bus(Name=TEST_BUS_NAME)
        assert response["Name"] == TEST_BUS_NAME
