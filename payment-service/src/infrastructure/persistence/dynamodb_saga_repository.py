"""
DynamoDB Saga Repository - Persistence adapter

Implements SagaRepository port using DynamoDB.
Handles saga state persistence and retrieval.
"""

import os
from typing import Optional, List
import boto3
from botocore.exceptions import ClientError

from ...domain.ports import SagaRepository
from ...domain.payment_saga import PaymentSaga
from ...domain.value_objects import SagaId, BookingId
from .saga_mapper import SagaMapper


class DynamoDBSagaRepository(SagaRepository):
    """DynamoDB implementation of SagaRepository"""
    
    def __init__(self, table_name: Optional[str] = None):
        """
        Initialize repository
        
        Args:
            table_name: DynamoDB table name (defaults to env var)
        """
        self.table_name = table_name or os.getenv(
            "DYNAMODB_SAGA_TABLE",
            "payment-sagas"
        )
        
        # Configure DynamoDB client for LocalStack
        endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        self.dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test")
        )
        
        self.table = self.dynamodb.Table(self.table_name)
        self.mapper = SagaMapper()
    
    async def save(self, saga: PaymentSaga) -> PaymentSaga:
        """
        Save saga state to DynamoDB
        
        Args:
            saga: Saga to persist
            
        Returns:
            Persisted saga
            
        Raises:
            Exception: If save fails
        """
        try:
            item = self.mapper.to_dynamodb(saga)
            self.table.put_item(Item=item)
            return saga
        except ClientError as e:
            raise Exception(f"Failed to save saga: {e.response['Error']['Message']}")
    
    async def find_by_id(self, saga_id: SagaId) -> Optional[PaymentSaga]:
        """
        Find saga by ID
        
        Args:
            saga_id: Saga identifier
            
        Returns:
            Saga if found, None otherwise
        """
        try:
            response = self.table.get_item(
                Key={
                    "PK": f"SAGA#{saga_id.value}",
                    "SK": f"SAGA#{saga_id.value}"
                }
            )
            
            if "Item" not in response:
                return None
            
            return self.mapper.from_dynamodb(response["Item"])
        except ClientError as e:
            raise Exception(f"Failed to find saga: {e.response['Error']['Message']}")
    
    async def find_by_booking_id(
        self,
        booking_id: BookingId
    ) -> Optional[PaymentSaga]:
        """
        Find saga by booking ID using GSI
        
        Args:
            booking_id: Booking identifier
            
        Returns:
            Saga if found, None otherwise
        """
        try:
            response = self.table.query(
                IndexName="BookingIdIndex",
                KeyConditionExpression="bookingId = :booking_id",
                ExpressionAttributeValues={
                    ":booking_id": booking_id.value
                },
                Limit=1
            )
            
            if not response.get("Items"):
                return None
            
            return self.mapper.from_dynamodb(response["Items"][0])
        except ClientError as e:
            raise Exception(f"Failed to find saga by booking: {e.response['Error']['Message']}")
    
    async def find_all(
        self,
        limit: int = 100,
        last_key: Optional[str] = None
    ) -> tuple[List[PaymentSaga], Optional[str]]:
        """
        Find all sagas with pagination
        
        Args:
            limit: Maximum number of sagas to return
            last_key: Pagination token (sagaId)
            
        Returns:
            Tuple of (sagas, next_page_token)
        """
        try:
            scan_kwargs = {
                "Limit": limit,
                "FilterExpression": "begins_with(PK, :pk_prefix)",
                "ExpressionAttributeValues": {
                    ":pk_prefix": "SAGA#"
                }
            }
            
            if last_key:
                scan_kwargs["ExclusiveStartKey"] = {
                    "PK": f"SAGA#{last_key}",
                    "SK": f"SAGA#{last_key}"
                }
            
            response = self.table.scan(**scan_kwargs)
            
            sagas = [
                self.mapper.from_dynamodb(item)
                for item in response.get("Items", [])
            ]
            
            # Extract next page token
            next_key = None
            if "LastEvaluatedKey" in response:
                # Extract sagaId from PK
                pk = response["LastEvaluatedKey"]["PK"]
                next_key = pk.replace("SAGA#", "")
            
            return sagas, next_key
        except ClientError as e:
            raise Exception(f"Failed to find all sagas: {e.response['Error']['Message']}")
