# Project Structure

## Repository Organization

```
.
├── event-service/          # Java/Spring Boot - Hexagonal Architecture
├── booking-service/        # Node.js/TypeScript - Hexagonal + CQRS
├── payment-service/        # Python/FastAPI - Saga Pattern
├── notification-service/   # Python/FastAPI - Buffer Pattern
├── localstack-data/        # LocalStack persistence (not committed)
├── docker-compose.yml      # LocalStack configuration
├── challenge.md            # Project documentation
└── .env                    # Environment variables (not committed)
```

## Service Architecture

### Event Service (Hexagonal Architecture)
```
event-service/
├── src/main/java/
│   ├── domain/           # Core business logic (ports)
│   │   ├── model/        # Aggregates, Value Objects
│   │   ├── port/         # Interfaces (in/out)
│   │   └── service/      # Domain services
│   ├── application/      # Use cases
│   └── infrastructure/   # Adapters (out)
│       ├── persistence/  # PostgreSQL adapter
│       ├── messaging/    # EventBridge adapter
│       └── api/          # REST controllers (in)
└── pom.xml
```

### Booking Service (Hexagonal + CQRS)
```
booking-service/
├── src/
│   ├── domain/           # Core business logic
│   │   ├── model/        # Aggregates
│   │   ├── commands/     # Write operations
│   │   └── queries/      # Read operations
│   ├── application/      # Use cases
│   │   ├── command/      # Command handlers
│   │   └── query/        # Query handlers
│   └── infrastructure/   # Adapters
│       ├── persistence/  # DynamoDB (write + read models)
│       ├── messaging/    # EventBridge
│       └── api/          # REST/GraphQL
└── package.json
```

### Payment Service (Saga Pattern)
```
payment-service/
├── src/
│   ├── domain/           # Saga orchestration logic
│   │   ├── saga/         # Saga state machine
│   │   └── compensation/ # Rollback handlers
│   ├── application/      # Saga coordinator
│   └── infrastructure/   # Adapters
│       ├── persistence/  # DynamoDB (saga state)
│       ├── messaging/    # EventBridge + SQS
│       └── api/          # REST endpoints
└── requirements.txt
```

### Notification Service (Buffer Pattern)
```
notification-service/
├── src/
│   ├── domain/           # Notification logic
│   ├── application/      # Message processing
│   └── infrastructure/   # Adapters
│       ├── queue/        # SQS consumer
│       ├── email/        # Email sender (mock)
│       └── lambda/       # Lambda handlers
└── requirements.txt
```

## Bounded Contexts (DDD)

Each service represents a bounded context with clear boundaries:

- **Event Context**: Events, venues, capacity management
- **Booking Context**: Reservations, tickets, booking lifecycle
- **Payment Context**: Transactions, saga orchestration, compensation
- **Notification Context**: Email delivery, notification buffering

## Data Storage Patterns

- **Event Service**: PostgreSQL (RDS) - relational data for events/venues
- **Booking Service**: DynamoDB - separate tables for write/read models with GSI
- **Payment Service**: DynamoDB - saga state persistence
- **Notification Service**: SQS - message buffering with DLQ

## Communication Patterns

- **Synchronous**: REST APIs for direct service calls
- **Asynchronous**: EventBridge for domain events, SQS for buffering
- **Event Types**: EventCreated, BookingCreated, BookingConfirmed, PaymentProcessed, NotificationSent

## Configuration Files

- `.env`: Environment variables (LocalStack token, AWS config)
- `docker-compose.yml`: LocalStack service definition
- `.gitignore`: Excludes localstack-data, .env, node_modules, etc.
