#!/bin/bash

# Initialize DynamoDB table for Payment Service
# Creates payment-sagas table with GSI for booking queries

set -e

ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
TABLE_NAME="payment-sagas"

echo "🚀 Initializing DynamoDB for Payment Service..."
echo "📍 Endpoint: $ENDPOINT_URL"
echo "🌍 Region: $REGION"
echo "📊 Table: $TABLE_NAME"

# Check if table exists
if awslocal dynamodb describe-table --table-name $TABLE_NAME --endpoint-url $ENDPOINT_URL 2>/dev/null; then
    echo "✅ Table $TABLE_NAME already exists"
    exit 0
fi

# Create table with GSI
echo "📝 Creating table $TABLE_NAME..."

awslocal dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
        AttributeName=bookingId,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"BookingIdIndex\",
                \"KeySchema\": [
                    {\"AttributeName\": \"bookingId\", \"KeyType\": \"HASH\"}
                ],
                \"Projection\": {
                    \"ProjectionType\": \"ALL\"
                },
                \"ProvisionedThroughput\": {
                    \"ReadCapacityUnits\": 5,
                    \"WriteCapacityUnits\": 5
                }
            }
        ]" \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url $ENDPOINT_URL \
    --region $REGION

echo "✅ Table $TABLE_NAME created successfully!"
echo ""
echo "📋 Table structure:"
echo "   - PK: SAGA#{sagaId} (Partition Key)"
echo "   - SK: SAGA#{sagaId} (Sort Key)"
echo "   - GSI: BookingIdIndex (bookingId)"
echo ""
echo "🎯 Ready to store saga state!"
