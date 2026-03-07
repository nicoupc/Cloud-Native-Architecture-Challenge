#!/bin/bash

# Initialize SQS queues for Notification Service
# Run this script after starting LocalStack

set -e

ENDPOINT_URL="http://localhost:4566"
REGION="us-east-1"

echo "🚀 Initializing SQS queues for Notification Service..."

# Create Dead Letter Queue first
echo "📦 Creating Dead Letter Queue..."
DLQ_URL=$(aws --endpoint-url=$ENDPOINT_URL sqs create-queue \
  --queue-name notification-dlq \
  --region $REGION \
  --attributes MessageRetentionPeriod=1209600 \
  --query 'QueueUrl' \
  --output text)

echo "✅ DLQ created: $DLQ_URL"

# Get DLQ ARN
DLQ_ARN=$(aws --endpoint-url=$ENDPOINT_URL sqs get-queue-attributes \
  --queue-url $DLQ_URL \
  --attribute-names QueueArn \
  --region $REGION \
  --query 'Attributes.QueueArn' \
  --output text)

echo "📋 DLQ ARN: $DLQ_ARN"

# Create main queue with DLQ redrive policy
echo "📦 Creating main notification queue..."
QUEUE_URL=$(aws --endpoint-url=$ENDPOINT_URL sqs create-queue \
  --queue-name notification-queue \
  --region $REGION \
  --attributes \
    VisibilityTimeout=30,\
MessageRetentionPeriod=345600,\
ReceiveMessageWaitTimeSeconds=20,\
RedrivePolicy="{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}" \
  --query 'QueueUrl' \
  --output text)

echo "✅ Main queue created: $QUEUE_URL"

# List queues
echo ""
echo "📋 Available queues:"
aws --endpoint-url=$ENDPOINT_URL sqs list-queues --region $REGION

echo ""
echo "✅ SQS initialization complete!"
echo ""
echo "Queue Configuration:"
echo "  - Main Queue: notification-queue"
echo "  - DLQ: notification-dlq"
echo "  - Visibility Timeout: 30 seconds"
echo "  - Message Retention: 4 days (main), 14 days (DLQ)"
echo "  - Max Receive Count: 3 (then moves to DLQ)"
echo "  - Long Polling: 20 seconds"
