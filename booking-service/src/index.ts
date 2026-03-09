import express from 'express';
import { logger } from './infrastructure/logging/logger';
import { createDynamoDBClient, createEventBridgeClient, createSQSClient, config } from './infrastructure/config/aws-config';
import { DynamoDBBookingRepository } from './infrastructure/persistence/DynamoDBBookingRepository';
import { DynamoDBBookingQueryRepository } from './infrastructure/persistence/DynamoDBBookingQueryRepository';
import { DynamoDBAvailabilityRepository } from './infrastructure/persistence/DynamoDBAvailabilityRepository';
import { EventBridgePublisher } from './infrastructure/messaging/EventBridgePublisher';
import { SqsEventConsumer } from './infrastructure/messaging/SqsEventConsumer';
import { CreateBookingHandler } from './application/command/CreateBookingHandler';
import { ConfirmBookingHandler } from './application/command/ConfirmBookingHandler';
import { CancelBookingHandler } from './application/command/CancelBookingHandler';
import { UpdateAvailabilityHandler } from './application/command/UpdateAvailabilityHandler';
import { CancelEventBookingsHandler } from './application/command/CancelEventBookingsHandler';
import { GetBookingByIdHandler } from './application/query/GetBookingByIdHandler';
import { GetBookingsByUserHandler } from './application/query/GetBookingsByUserHandler';
import { GetBookingsByEventHandler } from './application/query/GetBookingsByEventHandler';
import { BookingController } from './infrastructure/api/BookingController';

/**
 * Main Application Entry Point
 * 
 * Dependency Injection (Manual):
 * 1. Create infrastructure adapters (DynamoDB, EventBridge)
 * 2. Create application handlers (inject dependencies)
 * 3. Create API controllers (inject handlers)
 * 4. Start Express server
 * 
 * Why manual DI?
 * - Simple and explicit
 * - No framework magic
 * - Easy to understand for learning
 * 
 * In production, you might use:
 * - InversifyJS
 * - TypeDI
 * - NestJS (has built-in DI)
 */

async function bootstrap() {
  logger.info('🚀 Starting Booking Service...');

  // 1. Create AWS clients
  const dynamoClient = createDynamoDBClient();
  const eventBridgeClient = createEventBridgeClient();
  const sqsClient = createSQSClient();

  // 2. Create infrastructure adapters (OUTPUT ports)
  const bookingRepository = new DynamoDBBookingRepository(
    dynamoClient,
    config.dynamodb.tableName
  );

  const bookingQueryRepository = new DynamoDBBookingQueryRepository(
    dynamoClient,
    config.dynamodb.tableName
  );

  const eventPublisher = new EventBridgePublisher(
    eventBridgeClient,
    config.eventbridge.eventBusName,
    config.eventbridge.source
  );

  const availabilityRepository = new DynamoDBAvailabilityRepository(
    dynamoClient,
    config.availability.tableName
  );

  // 3. Create application handlers (inject dependencies)
  // Command Handlers (Write Side)
  const createBookingHandler = new CreateBookingHandler(
    bookingRepository,
    eventPublisher,
    availabilityRepository
  );

  const confirmBookingHandler = new ConfirmBookingHandler(
    bookingRepository,
    eventPublisher
  );

  const cancelBookingHandler = new CancelBookingHandler(
    bookingRepository,
    eventPublisher
  );

  // Query Handlers (Read Side)
  const getBookingByIdHandler = new GetBookingByIdHandler(
    bookingQueryRepository
  );

  const getBookingsByUserHandler = new GetBookingsByUserHandler(
    bookingQueryRepository
  );

  const getBookingsByEventHandler = new GetBookingsByEventHandler(
    bookingQueryRepository
  );

  // 4. Create API controller (INPUT port)
  const bookingController = new BookingController(
    createBookingHandler,
    confirmBookingHandler,
    cancelBookingHandler,
    getBookingByIdHandler,
    getBookingsByUserHandler,
    getBookingsByEventHandler
  );

  // 5. Create SQS Event Consumer (INPUT port - Event Listener)
  const updateAvailabilityHandler = new UpdateAvailabilityHandler(availabilityRepository);
  const cancelEventBookingsHandler = new CancelEventBookingsHandler(
    availabilityRepository,
    bookingQueryRepository,
    bookingRepository,
    eventPublisher
  );
  const sqsConsumer = new SqsEventConsumer(
    sqsClient,
    config.sqs.queueUrl,
    updateAvailabilityHandler,
    cancelEventBookingsHandler
  );

  // 6. Setup Express server
  const app = express();

  // Middleware
  app.use(express.json());

  // Health check
  app.get('/health', (_req, res) => {
    res.json({
      status: 'healthy',
      service: 'booking-service',
      timestamp: new Date().toISOString(),
    });
  });

  // API routes
  app.use('/api/v1', bookingController.getRouter());

  // Start server
  const port = config.server.port;
  app.listen(port, () => {
    logger.info('✅ Booking Service started successfully!');
    logger.info(`📡 Server listening on port ${port}`);
    logger.info(`🏥 Health check: http://localhost:${port}/health`);
    logger.info(`📚 API base URL: http://localhost:${port}/api/v1`);
    logger.info('');
    logger.info('📋 Available endpoints:');
    logger.info('   POST   /api/v1/bookings');
    logger.info('   POST   /api/v1/bookings/:id/confirm');
    logger.info('   POST   /api/v1/bookings/:id/cancel');
    logger.info('   GET    /api/v1/bookings/:id');
    logger.info('   GET    /api/v1/bookings/user/:userId');
    logger.info('   GET    /api/v1/bookings/event/:eventId');
    console.log('');
    // Start SQS consumer in background
    sqsConsumer.start().catch(err => console.error('SQS Consumer error:', err));
  });
}

// Start the application
bootstrap().catch(error => {
  console.error('❌ Failed to start Booking Service:', error);
  process.exit(1);
});
