import logging
import os
import boto3

logger = logging.getLogger("payment-service")


def setup_cloudwatch_logging() -> logging.Logger:
    """Setup CloudWatch logging via LocalStack."""
    endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    log_group = "/aws/payment-service"

    try:
        from watchtower import CloudWatchLogHandler

        logs_client = boto3.client(
            "logs",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        )

        # Create log group if not exists
        try:
            logs_client.create_log_group(logGroupName=log_group)
        except logs_client.exceptions.ResourceAlreadyExistsException:
            pass

        handler = CloudWatchLogHandler(
            log_group_name=log_group,
            log_stream_name="payment-service",
            boto3_client=logs_client,
            create_log_group=False,
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.info("CloudWatch logging enabled for payment-service")
    except ImportError:
        logger.warning("watchtower not installed, CloudWatch logging disabled")
    except Exception as e:
        logger.warning(f"CloudWatch logging setup failed: {e}, using console only")

    return logger
