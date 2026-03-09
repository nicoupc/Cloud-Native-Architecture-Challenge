"""
Tests for SQSConsumer
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from botocore.exceptions import ClientError

from src.infrastructure.queue.sqs_consumer import SQSConsumer


QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789/test-queue"


def _make_sqs_message(body: str, message_id: str = "msg-1", receipt_handle: str = "rh-1") -> dict:
    return {
        "MessageId": message_id,
        "ReceiptHandle": receipt_handle,
        "Body": body,
    }


@pytest.mark.asyncio
class TestSQSConsumerInit:
    """Tests for SQSConsumer initialization"""

    @patch("src.infrastructure.queue.sqs_consumer.boto3")
    def test_default_initialization(self, mock_boto3):
        processor = AsyncMock()
        consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)

        assert consumer.queue_url == QUEUE_URL
        assert consumer.processor is processor
        assert consumer.max_messages == 10
        assert consumer.wait_time_seconds == 20
        assert consumer.visibility_timeout == 30
        assert consumer.running is False
        mock_boto3.client.assert_called_once_with(
            "sqs", endpoint_url=None, region_name="us-east-1"
        )

    @patch("src.infrastructure.queue.sqs_consumer.boto3")
    def test_custom_initialization(self, mock_boto3):
        processor = AsyncMock()
        consumer = SQSConsumer(
            queue_url=QUEUE_URL,
            processor=processor,
            endpoint_url="http://localhost:4566",
            region_name="eu-west-1",
            max_messages=5,
            wait_time_seconds=10,
            visibility_timeout=60,
            rate_limit_per_second=2.0,
            rate_limit_burst=4.0,
        )

        assert consumer.max_messages == 5
        assert consumer.wait_time_seconds == 10
        assert consumer.visibility_timeout == 60
        mock_boto3.client.assert_called_once_with(
            "sqs", endpoint_url="http://localhost:4566", region_name="eu-west-1"
        )


@pytest.mark.asyncio
class TestSQSConsumerPollAndProcess:
    """Tests for _poll_and_process"""

    async def test_empty_receive_returns_no_messages(self):
        """When SQS returns no messages, nothing is processed"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.sqs.receive_message.return_value = {"Messages": []}

            await consumer._poll_and_process()

            processor.process_message.assert_not_called()

    async def test_empty_receive_no_messages_key(self):
        """When SQS response has no Messages key at all"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.sqs.receive_message.return_value = {}

            await consumer._poll_and_process()

            processor.process_message.assert_not_called()

    async def test_receive_calls_sqs_with_correct_params(self):
        """receive_message is called with configured parameters"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(
                queue_url=QUEUE_URL,
                processor=processor,
                max_messages=5,
                wait_time_seconds=10,
                visibility_timeout=60,
            )
            consumer.sqs = MagicMock()
            consumer.sqs.receive_message.return_value = {}

            await consumer._poll_and_process()

            consumer.sqs.receive_message.assert_called_once_with(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=5,
                WaitTimeSeconds=10,
                VisibilityTimeout=60,
                AttributeNames=["All"],
                MessageAttributeNames=["All"],
            )

    async def test_process_valid_message_and_delete(self):
        """A valid message is processed and deleted on success"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            processor.process_message.return_value = True

            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.rate_limiter = AsyncMock()

            body = json.dumps({"type": "BOOKING_CONFIRMED", "email": "a@b.com"})
            msg = _make_sqs_message(body)
            consumer.sqs.receive_message.return_value = {"Messages": [msg]}

            await consumer._poll_and_process()

            processor.process_message.assert_called_once_with(body)
            consumer.sqs.delete_message.assert_called_once_with(
                QueueUrl=QUEUE_URL, ReceiptHandle="rh-1"
            )

    async def test_message_not_deleted_on_processing_failure(self):
        """When processor returns False, message is NOT deleted"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            processor.process_message.return_value = False

            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.rate_limiter = AsyncMock()

            msg = _make_sqs_message('{"type": "BOOKING_CONFIRMED"}')
            consumer.sqs.receive_message.return_value = {"Messages": [msg]}

            await consumer._poll_and_process()

            consumer.sqs.delete_message.assert_not_called()

    async def test_multiple_messages_processed_in_order(self):
        """All messages in a batch are processed with rate limiting"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            processor.process_message.return_value = True

            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.rate_limiter = AsyncMock()

            msgs = [
                _make_sqs_message('{"id":1}', "msg-1", "rh-1"),
                _make_sqs_message('{"id":2}', "msg-2", "rh-2"),
                _make_sqs_message('{"id":3}', "msg-3", "rh-3"),
            ]
            consumer.sqs.receive_message.return_value = {"Messages": msgs}

            await consumer._poll_and_process()

            assert processor.process_message.call_count == 3
            assert consumer.sqs.delete_message.call_count == 3
            assert consumer.rate_limiter.acquire.call_count == 3

    async def test_client_error_during_receive(self):
        """ClientError from SQS receive_message is handled gracefully"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.sqs.receive_message.side_effect = ClientError(
                {"Error": {"Code": "AWS.SimpleQueueService.NonExistentQueue", "Message": "boom"}},
                "ReceiveMessage",
            )

            # Should not raise
            await consumer._poll_and_process()
            processor.process_message.assert_not_called()

    async def test_generic_error_during_receive(self):
        """Generic exception from receive_message is handled gracefully"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.sqs.receive_message.side_effect = RuntimeError("network error")

            await consumer._poll_and_process()
            processor.process_message.assert_not_called()


@pytest.mark.asyncio
class TestSQSConsumerProcessMessage:
    """Tests for _process_message"""

    async def test_successful_processing_deletes_message(self):
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            processor.process_message.return_value = True
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()

            msg = _make_sqs_message('{"ok": true}')
            await consumer._process_message(msg)

            processor.process_message.assert_called_once_with('{"ok": true}')
            consumer.sqs.delete_message.assert_called_once_with(
                QueueUrl=QUEUE_URL, ReceiptHandle="rh-1"
            )

    async def test_failed_processing_does_not_delete(self):
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            processor.process_message.return_value = False
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()

            msg = _make_sqs_message("bad data")
            await consumer._process_message(msg)

            consumer.sqs.delete_message.assert_not_called()

    async def test_exception_in_processor_is_caught(self):
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            processor.process_message.side_effect = Exception("processor crash")
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()

            msg = _make_sqs_message("body")
            # Should not raise
            await consumer._process_message(msg)
            consumer.sqs.delete_message.assert_not_called()

    async def test_message_with_missing_body_uses_default(self):
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            processor.process_message.return_value = True
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()

            msg = {"MessageId": "msg-1", "ReceiptHandle": "rh-1"}
            await consumer._process_message(msg)

            processor.process_message.assert_called_once_with("")


@pytest.mark.asyncio
class TestSQSConsumerDeleteMessage:
    """Tests for _delete_message"""

    async def test_successful_delete(self):
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()

            await consumer._delete_message("rh-abc")

            consumer.sqs.delete_message.assert_called_once_with(
                QueueUrl=QUEUE_URL, ReceiptHandle="rh-abc"
            )

    async def test_client_error_on_delete_is_handled(self):
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.sqs = MagicMock()
            consumer.sqs.delete_message.side_effect = ClientError(
                {"Error": {"Code": "ReceiptHandleIsInvalid", "Message": "bad handle"}},
                "DeleteMessage",
            )

            # Should not raise
            await consumer._delete_message("bad-handle")


@pytest.mark.asyncio
class TestSQSConsumerStartStop:
    """Tests for start/stop lifecycle"""

    def test_stop_sets_running_false(self):
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)
            consumer.running = True
            consumer.stop()
            assert consumer.running is False

    async def test_start_sets_running_true_and_polls(self):
        """start() sets running=True and calls _poll_and_process in loop"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"):
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)

            call_count = 0

            async def fake_poll():
                nonlocal call_count
                call_count += 1
                if call_count >= 3:
                    consumer.stop()

            consumer._poll_and_process = fake_poll

            await consumer.start()

            assert call_count == 3
            assert consumer.running is False

    async def test_start_retries_on_exception(self):
        """start() catches exceptions and retries after sleep"""
        with patch("src.infrastructure.queue.sqs_consumer.boto3"), \
             patch("src.infrastructure.queue.sqs_consumer.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            processor = AsyncMock()
            consumer = SQSConsumer(queue_url=QUEUE_URL, processor=processor)

            call_count = 0

            async def failing_poll():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise RuntimeError("temporary failure")
                consumer.stop()

            consumer._poll_and_process = failing_poll

            await consumer.start()

            assert call_count == 2
            mock_sleep.assert_called_once_with(5)
