# 📊 Progress Tracker - Cloud Native Architecture Challenge

## 🎯 Objetivo General
Implementar 4 microservicios con diferentes patrones arquitectónicos para demostrar su uso práctico en un sistema distribuido real.

---

## 📈 Progreso General

```
Fase 1 - Event Service:        ███████████████████░  95%
Fase 2 - Booking Service:      ████████████████████ 100%
Fase 3 - Payment Service:      ████████████████████ 100%
Fase 4 - Notification Service: ████████████████████ 100%
Fase 5 - Integración Final:    ██████████░░░░░░░░░░  50%
-------------------------------------------
TOTAL:                         █████████████████░░░  89%
```

---

## ✅ Fase 1: Event Service — Hexagonal Architecture — COMPLETADA (95%)

**Tecnología:** Java 17 + Spring Boot  
**Patrón:** Hexagonal Architecture (Ports & Adapters)  
**Puerto:** 8080

### ✅ Implementado:
- [x] Domain Layer: Event aggregate, Value Objects (Capacity, Price, EventId), Ports
- [x] Application Layer: CreateEventService, PublishEventService, CancelEventService, GetEventService
- [x] Infrastructure Layer: PostgreSQL adapter (RDS LocalStack), EventBridge adapter, REST API
- [x] 6 endpoints: `POST /events`, `GET /events`, `GET /events/{id}`, `POST /events/{id}/publish`, `POST /events/{id}/cancel`, `GET /events/health`
- [x] GlobalExceptionHandler: 404 (not found), 409 (invalid state), 400 (bad request)
- [x] Bugs corregidos: domain events usaban UUID random, reconstruct() no restauraba timestamps, controller generaba venueId dummy
- [x] 10 tests unitarios pasando
- [x] Scripts: `init-localstack.sh` (RDS), `init-eventbridge.sh` (EventBridge)
- [x] README con instrucciones Git Bash paso a paso ✅

### ⏳ Pendiente (opcional):
- [ ] Value Objects EventDate y Location (mejora de modelado)
- [ ] Venue aggregate
- [ ] Tests de integración con Testcontainers

---

## ✅ Fase 2: Booking Service — CQRS + Hexagonal Architecture — COMPLETADA (100%)

**Tecnología:** TypeScript + Node.js  
**Patrón:** CQRS (Command Query Responsibility Segregation) + Hexagonal Architecture  
**Puerto:** 3001

### ✅ Implementado:
- [x] Domain Layer: Booking aggregate, Value Objects (BookingId, UserId, EventId, BookingStatus, TicketQuantity, TotalPrice), Domain Events, Ports, Excepciones
- [x] Application Layer — Commands: CreateBookingCommand, ConfirmBookingCommand, CancelBookingCommand + sus Handlers
- [x] Application Layer — Queries: GetBookingByIdQuery, GetBookingsByUserQuery, GetBookingsByEventQuery + sus Handlers
- [x] Infrastructure Layer: DynamoDB Write Model, DynamoDB Read Model con GSI, BookingMapper, EventBridge Publisher
- [x] 6 endpoints REST: `POST /bookings`, `POST /bookings/:id/confirm`, `POST /bookings/:id/cancel`, `GET /bookings/:id`, `GET /bookings/user/:userId`, `GET /bookings/event/:eventId`
- [x] 41 tests unitarios pasando
- [x] Script: `init-dynamodb.sh` (tabla Bookings con GSI)
- [x] README con instrucciones Git Bash paso a paso ✅

---

## ✅ Fase 3: Payment Service — Saga Pattern — COMPLETADA (100%)

**Tecnología:** Python + FastAPI  
**Patrón:** Saga Pattern (Orchestration)  
**Puerto:** 3002

### ✅ Implementado:
- [x] Domain Layer: PaymentSaga aggregate, SagaState (8 estados), Value Objects (SagaId, BookingId, Amount, SagaStep), 9 Domain Events, 5 Ports, Excepciones
- [x] Application Layer: SagaOrchestrator con 4 pasos (RESERVE_BOOKING → PROCESS_PAYMENT → CONFIRM_BOOKING → SEND_NOTIFICATION), retry logic (3 intentos), compensación automática
- [x] Infrastructure Layer: DynamoDBSagaRepository, SagaMapper, EventBridgePublisher, MockPaymentGateway (80% éxito), HttpBookingServiceClient, EventBridgeNotificationClient
- [x] 4 endpoints REST: `POST /api/v1/sagas`, `GET /api/v1/sagas/{id}`, `GET /api/v1/sagas`, `POST /api/v1/sagas/{id}/compensate`
- [x] 74 tests unitarios pasando
- [x] Script: `init-payment-dynamodb.sh` (tabla payment-sagas con GSI)
- [x] README con instrucciones Git Bash paso a paso ✅

---

## ✅ Fase 4: Notification Service — Buffer Pattern — COMPLETADA (100%)

**Tecnología:** Python + asyncio  
**Patrón:** Buffer Pattern con SQS  
**Puerto:** N/A (consumidor de mensajes, no HTTP)

### ✅ Implementado:
- [x] Domain Layer: Notification aggregate, Value Objects (NotificationId, NotificationType, EmailAddress, EmailSubject, EmailBody, TemplateData), 6 Email Templates (BookingConfirmed, BookingCancelled, PaymentProcessed, PaymentFailed, EventPublished, EventCancelled), Domain Events (NotificationSent, NotificationFailed), Ports
- [x] Application Layer: NotificationProcessor (orquesta el flujo), MessageHandler (parsea mensajes de SQS y EventBridge)
- [x] Infrastructure Layer: SQSConsumer (long polling 20s, batch 10 msgs, visibility timeout 30s), MockEmailProvider (90% éxito)
- [x] **Rate Limiting:** Token Bucket (5 msgs/seg, burst 10) — configurable vía `RATE_LIMIT_PER_SECOND` y `RATE_LIMIT_BURST`
- [x] Dead Letter Queue (DLQ): mensajes pasan a DLQ tras 3 fallos
- [x] Graceful shutdown (SIGINT, SIGTERM)
- [x] 54 tests unitarios pasando (incluye 7 tests de rate limiter)
- [x] Cobertura >70%
- [x] Script: `init-notification-sqs.sh` (notification-queue + notification-dlq)
- [x] README con instrucciones Git Bash paso a paso ✅

---

## 🔄 Fase 5: Integración Final — EN PROGRESO (50%)

**Objetivo:** Conectar los 4 servicios para que funcionen juntos de punta a punta.

### Flujo completo:
```
1. Admin crea evento        → Event Service
2. Usuario hace reserva     → Booking Service (estado: PENDING)
3. Booking publica evento   → EventBridge → Payment Service
4. Payment procesa pago     → Mock Gateway
5. Payment confirma booking → Booking Service (estado: CONFIRMED)
6. Payment publica evento   → EventBridge → SQS → Notification Service
7. Notification envía email → Mock email (log)
```

### ✅ Completado:
- [x] Script `init-eventbridge-rules.sh` con 5 reglas EventBridge:
  - PaymentConfirmed → notification-queue
  - PaymentFailed → notification-queue
  - EventPublished → notification-queue
  - EventCancelled → notification-queue
  - BookingCreated → notification-queue
- [x] Payment Service se conecta a Booking Service (HTTP: confirm/cancel)
- [x] Colección Postman con todos los endpoints (`postman-collection.json`)

### ⏳ Pendiente:
- [ ] Prueba end-to-end con los 4 servicios levantados
- [ ] Documentar resultados del E2E test

---

## 📋 Entregables del Challenge

### Código ✅
- [x] 4 microservicios funcionales con sus patrones correctos
- [x] Tests unitarios (10 + 41 + 74 + 54 = **179 tests** en total)
- [x] Cobertura >70% en todos los servicios
- [x] Scripts de infraestructura (`init-*.sh`) para cada servicio
- [x] Docker Compose para levantar LocalStack
- [x] READMEs con instrucciones paso a paso (Git Bash)
- [x] Commits profesionales (Conventional Commits)

### Documentación ✅
- [x] Diagrama de arquitectura C4 (`docs/architecture-c4.md`)
- [x] Diagramas de secuencia para 4 flujos (`docs/sequence-diagrams.md`)
- [x] Colección Postman con todos los endpoints (`postman-collection.json`)

### Demo 🔄
- [x] Reglas EventBridge configuradas (script)
- [ ] Prueba end-to-end con resultados documentados

---

## 📝 Scripts de infraestructura (raíz del proyecto)

| Script | Servicio | ¿Qué crea? |
|--------|----------|------------|
| `init-localstack.sh` | Event Service | RDS PostgreSQL |
| `init-eventbridge.sh` | Event Service | Bus EventBridge |
| `init-eventbridge-rules.sh` | Integración | 5 reglas EventBridge (EDA) |
| `init-dynamodb.sh` | Booking Service | Tabla `Bookings` con GSI |
| `init-payment-dynamodb.sh` | Payment Service | Tabla `payment-sagas` con GSI |
| `init-notification-sqs.sh` | Notification Service | `notification-queue` + `notification-dlq` |
