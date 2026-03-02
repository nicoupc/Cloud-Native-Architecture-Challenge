# Technology Stack

## Languages & Frameworks

- **Event Service**: Java 17+ with Spring Boot
- **Booking Service**: TypeScript/Node.js 20+
- **Payment Service**: Python 3.11+ with FastAPI
- **Notification Service**: Python 3.11+ with FastAPI

## AWS Services (LocalStack)

All AWS services run locally via LocalStack on `http://localhost:4566`:

- **Compute**: Lambda
- **Storage**: DynamoDB, RDS (PostgreSQL)
- **Messaging**: EventBridge, SQS, SNS
- **API**: API Gateway
- **Monitoring**: CloudWatch Logs, X-Ray
- **Security**: IAM, Cognito, Secrets Manager
- **Orchestration**: Step Functions

## Development Tools

- **LocalStack**: AWS emulation (Pro version with student license)
- **Docker Compose**: Service orchestration
- **AWS CLI**: Use `awslocal` for LocalStack interactions

## Common Commands

### Environment Setup

```bash
# Start LocalStack and all services
docker-compose up -d

# Check LocalStack health
curl http://localhost:4566/_localstack/health

# Stop all services
docker-compose down
```

### AWS CLI (LocalStack)

```bash
# Use awslocal instead of aws for LocalStack
awslocal dynamodb list-tables
awslocal sqs list-queues
awslocal events list-event-buses

# Or use aws with --endpoint-url
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

### Service Development

```bash
# Event Service (Java/Spring Boot)
cd event-service
./mvnw spring-boot:run

# Booking Service (Node.js/TypeScript)
cd booking-service
npm install
npm run dev

# Payment Service (Python/FastAPI)
cd payment-service
pip install -r requirements.txt
uvicorn main:app --reload

# Notification Service (Python/FastAPI)
cd notification-service
pip install -r requirements.txt
uvicorn main:app --reload
```

### Testing

```bash
# Unit tests (run in each service directory)
npm test          # Node.js services
pytest            # Python services
./mvnw test       # Java services

# Integration tests with LocalStack
npm run test:integration
pytest tests/integration
```

## Configuration

- **Region**: `us-east-1` (default for consistency)
- **Persistence**: Enabled via `./localstack-data` volume
- **Debug Mode**: Enabled with `DEBUG=1` and `LS_LOG=trace`
- **Environment Variables**: Stored in `.env` (not committed)

## Key Environment Variables

```bash
LOCALSTACK_AUTH_TOKEN=<your-student-token>
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```
