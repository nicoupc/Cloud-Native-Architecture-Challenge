"""
SQS Consumer Integration Tests

Tests against real SQS in LocalStack.
Automatically skipped if LocalStack is not running.
"""

import json
import pytest
import boto3
from botocore.exceptions import ClientError

LOCALSTACK_URL = "http://localhost:4566"
QUEUE_NAME = "notification-integration-test-queue"


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
def sqs_client():
    """Create a real SQS client pointing to LocalStack."""
    return boto3.client(
        "sqs",
        endpoint_url=LOCALSTACK_URL,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture(scope="module")
def queue_url(sqs_client):
    """Create a test SQS queue and return its URL. Clean up after tests."""
    try:
        response = sqs_client.create_queue(
            QueueName=QUEUE_NAME,
            Attributes={
                "VisibilityTimeout": "30",
                "ReceiveMessageWaitTimeSeconds": "0",
            },
        )
        url = response["QueueUrl"]
    except ClientError:
        # Queue may already exist
        response = sqs_client.get_queue_url(QueueName=QUEUE_NAME)
        url = response["QueueUrl"]

    yield url

    try:
        sqs_client.delete_queue(QueueUrl=url)
    except Exception:
        pass


class TestSQSIntegration:
    """Integration tests for SQS message send/receive."""

    def test_send_and_receive_direct_message(self, sqs_client, queue_url):
        """Test sending and receiving a direct-format notification message."""
        message_body = json.dumps({
            "type": "BOOKING_CONFIRMED",
            "email": "test@example.com",
            "bookingId": "booking-int-001",
            "eventName": "Integration Test Concert",
            "ticketQuantity": 2,
            "totalPrice": 100.00,
        })

        sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)

        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5,
        )

        messages = response.get("Messages", [])
        assert len(messages) == 1

        received = json.loads(messages[0]["Body"])
        assert received["type"] == "BOOKING_CONFIRMED"
        assert received["email"] == "test@example.com"
        assert received["bookingId"] == "booking-int-001"

        # Clean up: delete the message
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=messages[0]["ReceiptHandle"],
        )

    def test_send_and_receive_eventbridge_format(self, sqs_client, queue_url):
        """Test sending and receiving an EventBridge-format message."""
        message_body = json.dumps({
            "detail-type": "BookingConfirmed",
            "source": "booking-service",
            "detail": {
                "userEmail": "eb-test@example.com",
                "bookingId": "booking-eb-001",
                "eventName": "EB Integration Concert",
                "ticketQuantity": 3,
                "totalPrice": 150.00,
            },
        })

        sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)

        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5,
        )

        messages = response.get("Messages", [])
        assert len(messages) == 1

        received = json.loads(messages[0]["Body"])
        assert received["detail-type"] == "BookingConfirmed"
        assert received["detail"]["userEmail"] == "eb-test@example.com"

        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=messages[0]["ReceiptHandle"],
        )

    def test_empty_queue_returns_no_messages(self, sqs_client, queue_url):
        """Test that an empty queue returns no messages."""
        # Purge any existing messages
        try:
            sqs_client.purge_queue(QueueUrl=queue_url)
        except ClientError:
            pass

        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
        )

        messages = response.get("Messages", [])
        assert len(messages) == 0

    def test_message_visibility_timeout(self, sqs_client, queue_url):
        """Test that messages become invisible after being received."""
        message_body = json.dumps({
            "type": "PAYMENT_PROCESSED",
            "email": "vis-test@example.com",
            "bookingId": "booking-vis-001",
        })

        sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)

        # First receive — should get the message
        resp1 = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=2,
            VisibilityTimeout=10,
        )
        assert len(resp1.get("Messages", [])) == 1

        # Immediate second receive — message should be invisible
        resp2 = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
        )
        assert len(resp2.get("Messages", [])) == 0

        # Clean up
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=resp1["Messages"][0]["ReceiptHandle"],
        )
