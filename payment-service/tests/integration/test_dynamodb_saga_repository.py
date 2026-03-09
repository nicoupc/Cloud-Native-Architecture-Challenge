"""
DynamoDB Saga Repository Integration Tests

Tests against real DynamoDB in LocalStack.
Automatically skipped if LocalStack is not running.
"""

import pytest
import asyncio
import boto3
from botocore.exceptions import ClientError

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.infrastructure.persistence.dynamodb_saga_repository import DynamoDBSagaRepository
from src.domain.payment_saga import PaymentSaga
from src.domain.value_objects import SagaId, BookingId, Amount

LOCALSTACK_URL = "http://localhost:4566"
TABLE_NAME = "payment-sagas-integration-test"


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
def dynamodb_client():
    """Create a real DynamoDB client pointing to LocalStack."""
    return boto3.client(
        "dynamodb",
        endpoint_url=LOCALSTACK_URL,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture(scope="module")
def dynamodb_table(dynamodb_client):
    """Create a test DynamoDB table matching init-payment-dynamodb.sh schema."""
    try:
        dynamodb_client.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "bookingId", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "BookingIdIndex",
                    "KeySchema": [
                        {"AttributeName": "bookingId", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                }
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )
        dynamodb_client.get_waiter("table_exists").wait(TableName=TABLE_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceInUseException":
            raise

    yield TABLE_NAME

    try:
        dynamodb_client.delete_table(TableName=TABLE_NAME)
    except Exception:
        pass


@pytest.fixture
def repository(dynamodb_table):
    """Create a DynamoDBSagaRepository pointing to the test table."""
    os.environ["AWS_ENDPOINT_URL"] = LOCALSTACK_URL
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    repo = DynamoDBSagaRepository(table_name=TABLE_NAME)
    return repo


def create_test_saga(booking_id_str: str = "booking-test-001") -> PaymentSaga:
    """Helper to create a test PaymentSaga."""
    return PaymentSaga.create(
        booking_id=BookingId(booking_id_str),
        amount=Amount(100.00, "USD"),
    )


class TestDynamoDBSagaRepository:
    """Integration tests for DynamoDBSagaRepository."""

    @pytest.mark.asyncio
    async def test_save_and_find_by_id(self, repository):
        """Test saving a saga and retrieving it by ID."""
        saga = create_test_saga("booking-save-001")

        saved = await repository.save(saga)
        assert saved.id == saga.id

        found = await repository.find_by_id(saga.id)

        assert found is not None
        assert found.id.value == saga.id.value
        assert found.booking_id.value == "booking-save-001"
        assert found.amount.value == 100.00
        assert found.amount.currency == "USD"
        assert found.state.value == "STARTED"
        assert len(found.steps) == 4

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository):
        """Test finding a non-existent saga returns None."""
        non_existent = SagaId.generate()
        found = await repository.find_by_id(non_existent)
        assert found is None

    @pytest.mark.asyncio
    async def test_find_by_booking_id(self, repository):
        """Test finding a saga by booking ID via GSI."""
        saga = create_test_saga("booking-gsi-001")
        await repository.save(saga)

        found = await repository.find_by_booking_id(BookingId("booking-gsi-001"))

        assert found is not None
        assert found.booking_id.value == "booking-gsi-001"
        assert found.id.value == saga.id.value

    @pytest.mark.asyncio
    async def test_find_by_booking_id_not_found(self, repository):
        """Test finding a non-existent booking ID returns None."""
        found = await repository.find_by_booking_id(BookingId("non-existent-booking"))
        assert found is None

    @pytest.mark.asyncio
    async def test_update_saga_state(self, repository):
        """Test updating saga state persists correctly."""
        saga = create_test_saga("booking-update-001")
        await repository.save(saga)

        # Advance the saga
        saga.start_current_step()
        saga.complete_current_step()
        await repository.save(saga)

        found = await repository.find_by_id(saga.id)
        assert found is not None
        assert found.current_step_index == 1
        assert found.steps[0].status == "COMPLETED"

    @pytest.mark.asyncio
    async def test_find_all(self, repository):
        """Test finding all sagas with pagination."""
        # Create a couple of sagas
        saga1 = create_test_saga("booking-all-001")
        saga2 = create_test_saga("booking-all-002")
        await repository.save(saga1)
        await repository.save(saga2)

        sagas, next_key = await repository.find_all(limit=100)
        assert len(sagas) >= 2
