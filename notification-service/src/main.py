"""
Notification Service Main Application

Entry point for the notification service consumer.
"""

import os
import asyncio
import logging
import signal
from dotenv import load_dotenv

from .application import NotificationProcessor
from .infrastructure import MockEmailProvider, SQSConsumer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Main notification service application"""
    
    def __init__(self):
        # Configuration from environment
        self.queue_url = os.getenv(
            "SQS_QUEUE_URL",
            "http://localhost:4566/000000000000/notification-queue"
        )
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        # Rate limiting configuration
        rate_limit = float(os.getenv("RATE_LIMIT_PER_SECOND", "5"))
        rate_limit_burst = float(os.getenv("RATE_LIMIT_BURST", "10"))
        
        # Initialize components
        self.email_provider = MockEmailProvider(success_rate=0.9)
        self.processor = NotificationProcessor(self.email_provider)
        self.consumer = SQSConsumer(
            queue_url=self.queue_url,
            processor=self.processor,
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            rate_limit_per_second=rate_limit,
            rate_limit_burst=rate_limit_burst
        )
        
        # Shutdown flag
        self.shutdown_event = asyncio.Event()
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating shutdown")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Run the service"""
        logger.info("Starting Notification Service")
        logger.info(f"Queue URL: {self.queue_url}")
        logger.info(f"Endpoint: {self.endpoint_url}")
        logger.info(f"Rate limit: {self.consumer.rate_limiter.rate} msgs/sec")
        
        # Start consumer
        consumer_task = asyncio.create_task(self.consumer.start())
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        
        # Stop consumer
        self.consumer.stop()
        await consumer_task
        
        logger.info("Notification Service stopped")


async def main():
    """Main entry point"""
    service = NotificationService()
    service.setup_signal_handlers()
    await service.run()


if __name__ == "__main__":
    asyncio.run(main())
