"""
SQS Consumer

Polls messages from SQS queue with long polling.
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError

from ...application import NotificationProcessor

logger = logging.getLogger(__name__)


class SQSConsumer:
    """
    SQS Consumer with long polling
    
    Implements Buffer Pattern by consuming messages from SQS queue.
    """
    
    def __init__(
        self,
        queue_url: str,
        processor: NotificationProcessor,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        max_messages: int = 10,
        wait_time_seconds: int = 20,
        visibility_timeout: int = 30
    ):
        """
        Initialize SQS consumer
        
        Args:
            queue_url: SQS queue URL
            processor: Notification processor
            endpoint_url: LocalStack endpoint (for testing)
            region_name: AWS region
            max_messages: Max messages per poll (1-10)
            wait_time_seconds: Long polling wait time (0-20)
            visibility_timeout: Message visibility timeout
        """
        self.queue_url = queue_url
        self.processor = processor
        self.max_messages = max_messages
        self.wait_time_seconds = wait_time_seconds
        self.visibility_timeout = visibility_timeout
        self.running = False
        
        # Initialize SQS client
        self.sqs = boto3.client(
            "sqs",
            endpoint_url=endpoint_url,
            region_name=region_name
        )

    
    async def start(self) -> None:
        """Start consuming messages"""
        self.running = True
        logger.info(f"Starting SQS consumer for queue: {self.queue_url}")
        
        while self.running:
            try:
                await self._poll_and_process()
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    def stop(self) -> None:
        """Stop consuming messages"""
        logger.info("Stopping SQS consumer")
        self.running = False
    
    async def _poll_and_process(self) -> None:
        """Poll messages and process them"""
        try:
            # Receive messages with long polling
            response = await asyncio.to_thread(
                self.sqs.receive_message,
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=self.max_messages,
                WaitTimeSeconds=self.wait_time_seconds,
                VisibilityTimeout=self.visibility_timeout,
                AttributeNames=["All"],
                MessageAttributeNames=["All"]
            )
            
            messages = response.get("Messages", [])
            
            if not messages:
                logger.debug("No messages received")
                return
            
            logger.info(f"Received {len(messages)} messages")
            
            # Process messages
            for message in messages:
                await self._process_message(message)
                
        except ClientError as e:
            logger.error(f"SQS client error: {e}")
        except Exception as e:
            logger.error(f"Error polling messages: {e}")
    
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Process a single message"""
        receipt_handle = message.get("ReceiptHandle")
        message_body = message.get("Body", "")
        message_id = message.get("MessageId", "unknown")
        
        try:
            logger.info(f"Processing message {message_id}")
            
            # Process message
            success = await self.processor.process_message(message_body)
            
            if success:
                # Delete message from queue
                await self._delete_message(receipt_handle)
                logger.info(f"Message {message_id} processed successfully")
            else:
                logger.warning(
                    f"Message {message_id} processing failed, "
                    "will retry after visibility timeout"
                )
                
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
    
    async def _delete_message(self, receipt_handle: str) -> None:
        """Delete message from queue"""
        try:
            await asyncio.to_thread(
                self.sqs.delete_message,
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
        except ClientError as e:
            logger.error(f"Failed to delete message: {e}")
