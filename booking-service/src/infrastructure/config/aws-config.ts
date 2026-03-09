import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { EventBridgeClient } from '@aws-sdk/client-eventbridge';
import { SQSClient } from '@aws-sdk/client-sqs';

/**
 * AWS Configuration for LocalStack
 * 
 * Why do we need this?
 * - In development: Connect to LocalStack (localhost:4566)
 * - In production: Connect to real AWS
 * - This file centralizes the configuration
 */

const isLocalStack = process.env.USE_LOCALSTACK !== 'false';
const localStackEndpoint = process.env.LOCALSTACK_ENDPOINT || 'http://localhost:4566';
const region = process.env.AWS_REGION || 'us-east-1';

/**
 * Common configuration for LocalStack
 */
const localStackConfig = {
  endpoint: localStackEndpoint,
  region,
  credentials: {
    accessKeyId: 'test',
    secretAccessKey: 'test',
  },
};

/**
 * Creates a DynamoDB client
 */
export function createDynamoDBClient(): DynamoDBClient {
  if (isLocalStack) {
    return new DynamoDBClient(localStackConfig);
  }

  // Production configuration (uses IAM roles)
  return new DynamoDBClient({ region });
}

/**
 * Creates an EventBridge client
 */
export function createEventBridgeClient(): EventBridgeClient {
  if (isLocalStack) {
    return new EventBridgeClient(localStackConfig);
  }

  // Production configuration (uses IAM roles)
  return new EventBridgeClient({ region });
}

/**
 * Creates an SQS client
 */
export function createSQSClient(): SQSClient {
  if (isLocalStack) {
    return new SQSClient(localStackConfig);
  }

  // Production configuration (uses IAM roles)
  return new SQSClient({ region });
}

/**
 * Configuration values
 */
export const config = {
  dynamodb: {
    tableName: process.env.DYNAMODB_TABLE_NAME || 'Bookings',
  },
  eventbridge: {
    eventBusName: process.env.EVENTBRIDGE_BUS_NAME || 'event-management-bus',
    source: 'booking-service',
  },
  sqs: {
    queueUrl: process.env.BOOKING_QUEUE_URL || 'http://localhost:4566/000000000000/booking-events-queue',
  },
  availability: {
    tableName: process.env.AVAILABILITY_TABLE_NAME || 'EventAvailability',
  },
  server: {
    port: parseInt(process.env.PORT || '3001', 10),
  },
};
