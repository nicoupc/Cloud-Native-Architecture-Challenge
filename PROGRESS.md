# 📊 Progress Tracker - Cloud Native Architecture Challenge

## 🎯 Objetivo General
Implementar 4 microservicios con diferentes patrones arquitectónicos para demostrar su uso práctico en un sistema distribuido real.

---

## 📈 Progreso General

```
Fase 1 - Event Service:        ████████████████████ 100%
Fase 2 - Booking Service:      ████████████████████ 100%
Fase 3 - Payment Service:      ████████████████████ 100%
Fase 4 - Notification Service: ████████████████████ 100%
Fase 5 - Integración Final:    ████████████████████ 100%
-------------------------------------------
TOTAL:                         ████████████████████ 100%
```

---

## ✅ Fase 1: Event Service — Hexagonal Architecture — COMPLETADA (100%)

**Tecnología:** Java 17 + Spring Boot  
**Patrón:** Hexagonal Architecture (Ports & Adapters)  
**Puerto:** 8080

### ✅ Implementado:
- [x] Domain Layer: Event aggregate, Venue aggregate, Value Objects (EventDate, Location, Capacity, Price, EventId, VenueId), Ports
- [x] Application Layer: CreateEventService, PublishEventService, CancelEventService, GetEventService, CreateVenueService, GetVenueService
- [x] Infrastructure Layer: PostgreSQL adapter (RDS LocalStack), EventBridge adapter, REST API
- [x] Event endpoints: `POST /events`, `GET /events`, `GET /events/{id}`, `POST /events/{id}/publish`, `POST /events/{id}/cancel`, `GET /events/health`
- [x] Venue endpoints: `POST /api/v1/venues`, `GET /api/v1/venues`, `GET /api/v1/venues/{id}`
- [x] GlobalExceptionHandler: 404 (not found), 409 (invalid state), 400 (bad request)
- [x] Flyway migrations: V1 (events table), V2 (venues table + location columns)
- [x] 34 tests unitarios + 3 integration tests pasando (37 total)
- [x] Validación @Valid con Bean Validation en EventController
- [x] CloudWatch observability (logback-spring.xml)
- [x] Scripts: `init-localstack.sh` (RDS), `init-eventbridge.sh` (EventBridge)
- [x] README con instrucciones Git Bash paso a paso ✅

---

## ✅ Fase 2: Booking Service — CQRS + Hexagonal Architecture — COMPLETADA (100%)

**Tecnología:** TypeScript + Node.js  
**Patrón:** CQRS (Command Query Responsibility Segregation) + Hexagonal Architecture  
**Puerto:** 3001

### ✅ Implementado:
- [x] Domain Layer: Booking aggregate, Value Objects (BookingId, UserId, EventId, BookingStatus, TicketQuantity, TotalPrice, TicketType, ReservationTime), BookingItem entity, Domain Events, Ports, Excepciones
- [x] Application Layer — Commands: CreateBookingCommand, ConfirmBookingCommand, CancelBookingCommand + sus Handlers
- [x] Application Layer — Queries: GetBookingByIdQuery, GetBookingsByUserQuery, GetBookingsByEventQuery + sus Handlers
- [x] Infrastructure Layer: DynamoDB Write Model, DynamoDB Read Model con GSI, BookingMapper, EventBridge Publisher
- [x] 6 endpoints REST: `POST /bookings`, `POST /bookings/:id/confirm`, `POST /bookings/:id/cancel`, `GET /bookings/:id`, `GET /bookings/user/:userId`, `GET /bookings/event/:eventId`
- [x] 195 tests unitarios + 7 integration tests (202 total, 27 suites)
- [x] EventBridge Consumer via SQS (EventCreated/EventCancelled)
- [x] EventAvailability tracking (DynamoDB)
- [x] Contract tests (API + Event schemas)
- [x] CloudWatch observability logger
- [x] Script: `init-dynamodb.sh` (tabla Bookings con GSI)
- [x] README con instrucciones Git Bash paso a paso ✅

---

## ✅ Fase 3: Payment Service — Saga Pattern — COMPLETADA (100%)

**Tecnología:** Python + FastAPI  
**Patrón:** Saga Pattern (Orchestration)  
**Puerto:** 3002

### ✅ Implementado:
- [x] Domain Layer: PaymentSaga aggregate con PaymentAttempt tracking, SagaState (8 estados), Value Objects (SagaId, BookingId, Amount, SagaStep), 9 Domain Events, 5 Ports, Excepciones
- [x] Application Layer: SagaOrchestrator con 4 pasos (RESERVE_BOOKING → PROCESS_PAYMENT → CONFIRM_BOOKING → SEND_NOTIFICATION), retry logic (3 intentos), compensación automática con refund real
- [x] Infrastructure Layer: DynamoDBSagaRepository, SagaMapper, EventBridgePublisher, MockPaymentGateway (80% éxito), HttpBookingServiceClient, EventBridgeNotificationClient
- [x] 4 endpoints REST: `POST /api/v1/sagas`, `GET /api/v1/sagas/{id}`, `GET /api/v1/sagas`, `POST /api/v1/sagas/{id}/compensate`
- [x] Payment refund implementado en compensación (usa PaymentGateway.refund_payment)
- [x] PaymentAttempt tracking: registra cada intento de pago con status y payment_id
- [x] 153 tests unitarios + 10 integration tests (163 total) — **84.60% cobertura**
- [x] Contract tests (event schemas + booking API)
- [x] CloudWatch observability logger
- [x] Script: `init-payment-dynamodb.sh` (tabla payment-sagas con GSI)
- [x] README con instrucciones Git Bash paso a paso ✅

---

## ✅ Fase 4: Notification Service — Buffer Pattern — COMPLETADA (100%)

**Tecnología:** Python + asyncio  
**Patrón:** Buffer Pattern con SQS  
**Puerto:** N/A (consumidor de mensajes, no HTTP)

### ✅ Implementado:
- [x] Domain Layer: Notification aggregate, Value Objects (NotificationId, NotificationType, EmailAddress, EmailSubject, EmailBody, TemplateData), 6 Email Templates (BookingConfirmed, BookingCancelled, PaymentProcessed, PaymentFailed, EventPublished, EventCancelled), Domain Events, Ports
- [x] Application Layer: NotificationProcessor (orquesta el flujo), MessageHandler (parsea mensajes de SQS y EventBridge) — todos los 6 tipos de evento mapeados correctamente
- [x] Infrastructure Layer: SQSConsumer (long polling 20s, batch 10 msgs, visibility timeout 30s), MockEmailProvider (90% éxito)
- [x] **Rate Limiting:** Token Bucket (5 msgs/seg, burst 10) — configurable vía `RATE_LIMIT_PER_SECOND` y `RATE_LIMIT_BURST`
- [x] Dead Letter Queue (DLQ): mensajes pasan a DLQ tras 3 fallos
- [x] Graceful shutdown (SIGINT, SIGTERM)
- [x] 73 tests unitarios + 4 integration tests (77 total)
- [x] Cobertura **78.04%** ✅
- [x] CloudWatch observability logger
- [x] Script: `init-notification-sqs.sh` (notification-queue + notification-dlq)
- [x] README con instrucciones Git Bash paso a paso ✅

---

## 🔄 Fase 5: Integración Final — EN PROGRESO (90%)

**Objetivo:** Conectar los 4 servicios para que funcionen juntos de punta a punta.

### Flujo completo:
```
1. Admin crea evento        → Event Service
2. Usuario hace reserva     → Booking Service (estado: PENDING)
3. Booking publica evento   → EventBridge → Payment Service
4. Payment procesa pago     → Mock Gateway (con tracking de intentos)
5. Payment confirma booking → Booking Service (estado: CONFIRMED)
6. Payment publica evento   → EventBridge → SQS → Notification Service
7. Notification envía email → Mock email (log)
```

### ✅ Completado:
- [x] Script `init-eventbridge-rules.sh` con 7 reglas EventBridge (5 notificación + 2 booking)
- [x] Payment Service se conecta a Booking Service (HTTP: confirm/cancel)
- [x] Colección Postman con todos los endpoints (`postman-collection.json`)
- [x] Script E2E test (`test-e2e.sh`) — prueba happy path, cancelación, y CQRS
- [x] Seed data script (`seed-data.sh`) para poblar datos de prueba
- [x] Flujo E2E verificado con Docker (saga completa funcional)
- [x] Integration tests con LocalStack en los 4 servicios
- [x] Contract tests entre servicios (Payment↔Booking)
- [x] CloudWatch observability en los 4 servicios
- [x] EventBridge consumer en Booking Service (availability tracking)

### ✅ Pendiente: Ninguno

---

## 📋 Entregables del Challenge

### Código ✅
- [x] 4 microservicios funcionales con sus patrones correctos
- [x] Tests unitarios + integración + contrato (37 + 202 + 163 + 77 = **479 tests** en total)
- [x] Cobertura >70% en todos los servicios (Payment 85%, Notification 78%, Booking ✅)
- [x] Integration tests con LocalStack (auto-skip si Docker no corre)
- [x] Contract tests entre servicios (Payment↔Booking API + event schemas)
- [x] Scripts de infraestructura (`init-*.sh`) para cada servicio
- [x] Docker Compose para levantar LocalStack
- [x] READMEs con instrucciones paso a paso (Git Bash)
- [x] Commits profesionales (Conventional Commits)

### Documentación ✅
- [x] Diagrama de arquitectura C4 (`docs/architecture-c4.md`)
- [x] Diagramas de secuencia para 4 flujos (`docs/sequence-diagrams.md`)
- [x] 6 Architecture Decision Records (`docs/adr/ADR-001` a `ADR-006`)
- [x] Colección Postman con todos los endpoints (`postman-collection.json`)

### Demo 🔄
- [x] Reglas EventBridge configuradas (script)
- [x] Script de seed data para datos de prueba
- [x] Prueba end-to-end con resultados documentados ✅

---

## 📝 Scripts de infraestructura (raíz del proyecto)

| Script | Servicio | ¿Qué crea? |
|--------|----------|------------|
| `init-localstack.sh` | Event Service | RDS PostgreSQL |
| `init-eventbridge.sh` | Event Service | Bus EventBridge |
| `init-eventbridge-rules.sh` | Integración | 7 reglas EventBridge (EDA) |
| `init-dynamodb.sh` | Booking Service | Tabla `Bookings` con GSI |
| `init-payment-dynamodb.sh` | Payment Service | Tabla `payment-sagas` con GSI |
| `init-notification-sqs.sh` | Notification Service | `notification-queue` + `notification-dlq` |
| `init-booking-sqs.sh` | Booking Service | `booking-events-queue` + `booking-events-dlq` + `EventAvailability` |
| `init-cloudwatch.sh` | Todos | 4 log groups CloudWatch |
| `seed-data.sh` | Todos | Datos de prueba para los 3 almacenes |
| `test-e2e.sh` | Todos | Prueba E2E del flujo completo |

---

## 📐 Architecture Decision Records (ADRs)

| ADR | Decisión |
|-----|----------|
| ADR-001 | Hexagonal Architecture para Event Service |
| ADR-002 | CQRS + DynamoDB para Booking Service |
| ADR-003 | Saga Orchestration para Payment Service |
| ADR-004 | Asyncio SQS Consumer para Notification Service |
| ADR-005 | Token Bucket Rate Limiting |
| ADR-006 | EventBridge como Bus Central de Eventos |
