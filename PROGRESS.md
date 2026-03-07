# 📊 Progress Tracker - Cloud Native Architecture Challenge

## 🎯 Objetivo General
Implementar 4 microservicios con diferentes patrones arquitectónicos para aprender cuándo y por qué usar cada uno.

---

## ✅ Fase 1: Event Service (Hexagonal Architecture) - COMPLETADA

### Estado: 85% ✅ (Funcional para el challenge)

#### ✅ Completado:
- [x] Configurar LocalStack con Docker Compose
- [x] Crear infraestructura básica (PostgreSQL RDS, EventBridge)
- [x] Implementar Event Service con Hexagonal Architecture
  - [x] Domain Layer (Event, Value Objects, Ports)
  - [x] Application Layer (CreateEventService, PublishEventService)
  - [x] Infrastructure Layer (PostgreSQL Adapter, EventBridge Adapter, REST API)
- [x] Probar creación de eventos y publicación a EventBridge
- [x] Tests unitarios básicos (10 tests pasando)
- [x] Git commits profesionales (Conventional Commits)

#### ⏳ Pendiente (opcional, se puede hacer después):
- [ ] Más REST endpoints (GET, PUT, DELETE)
- [ ] Global Exception Handler
- [ ] Tests de integración con Testcontainers
- [ ] Venue aggregate implementation

#### 📚 Aprendizajes Clave:
- ✅ Hexagonal Architecture (Ports & Adapters)
- ✅ Domain-Driven Design (Aggregates, Value Objects, Domain Events)
- ✅ Event-Driven Architecture (EventBridge)
- ✅ Transacciones distribuidas con @Transactional

---

## 🚀 Fase 2: Booking Service (CQRS + Hexagonal) - COMPLETADA

### Estado: 100% ✅

### Objetivos de Aprendizaje:
- [x] Implementar CQRS (Command Query Responsibility Segregation)
- [x] Usar DynamoDB con índices GSI
- [x] Separar Write Model y Read Model
- [x] Eventual Consistency entre modelos
- [x] Publicar eventos a EventBridge

### Implementación Completada:

#### ✅ Domain Layer (100%)
- [x] Value Objects: BookingId, UserId, EventId, BookingStatus, TicketQuantity, TotalPrice
- [x] Booking Aggregate con state transitions
- [x] Domain Events: BookingCreated, BookingConfirmed, BookingCancelled
- [x] Ports: BookingRepository (write), BookingQueryRepository (read), EventPublisher
- [x] Domain Exceptions: BookingNotFoundException, InvalidBookingStateException

#### ✅ Application Layer (100%)
- [x] Commands: CreateBookingCommand, ConfirmBookingCommand, CancelBookingCommand
- [x] Command Handlers: CreateBookingHandler, ConfirmBookingHandler, CancelBookingHandler
- [x] Queries: GetBookingByIdQuery, GetBookingsByUserQuery, GetBookingsByEventQuery
- [x] Query Handlers: GetBookingByIdHandler, GetBookingsByUserHandler, GetBookingsByEventHandler

#### ✅ Infrastructure Layer (100%)
- [x] DynamoDB Write Model: DynamoDBBookingRepository
- [x] DynamoDB Read Model: DynamoDBBookingQueryRepository con GSI
- [x] BookingMapper: Domain ↔ DynamoDB translation
- [x] EventBridge Publisher: EventBridgePublisher
- [x] AWS Configuration: LocalStack setup
- [x] REST API: BookingController con 6 endpoints
- [x] DTOs: CreateBookingRequest, BookingResponse
- [x] Application Bootstrap: index.ts con dependency injection

#### ✅ Testing (100%)
- [x] 41 unit tests passing
- [x] Domain model tests
- [x] Command handler tests
- [x] 100% code compiles without errors

#### ✅ Scripts y Configuración
- [x] init-dynamodb.sh: Script para crear tabla con GSI
- [x] .env.example: Configuración de ejemplo
- [x] README.md: Documentación completa con ejemplos

### 📚 Conceptos Aprendidos:
- ✅ CQRS: Separación clara entre Commands (write) y Queries (read)
- ✅ Write Model: Optimizado para validaciones con strong consistency
- ✅ Read Model: Optimizado para queries con GSI y eventual consistency
- ✅ DynamoDB GSI: Índices secundarios para queries eficientes
- ✅ Hexagonal Architecture: Ports & Adapters pattern
- ✅ Dependency Injection: Manual DI para claridad
- ✅ Event-Driven: Publicación de eventos a EventBridge

### 🎯 Próximos Pasos (Opcionales):
- [ ] Tests de integración con LocalStack
- [ ] Integración end-to-end con Event Service
- [ ] Consumer de eventos de EventBridge

---

## 🚀 Fase 3: Payment Service (Saga Pattern) - EN PROGRESO

### Estado: 0% ⏳

### Objetivos de Aprendizaje:
- [ ] Implementar Saga Pattern con orchestration
- [ ] Crear state machine para flujo de pago distribuido
- [ ] Implementar compensación automática en caso de fallos
- [ ] Coordinar múltiples servicios (Booking, Payment Gateway, Notification)
- [ ] Manejar idempotencia y reintentos
- [ ] Persistir estado de saga en DynamoDB

### Plan de Implementación:

#### Paso 1: Setup del Proyecto (30-45 min) ⏳
- [ ] Crear estructura de carpetas para Payment Service (Python/FastAPI)
- [ ] Configurar pyproject.toml o requirements.txt con dependencias
- [ ] Configurar estructura de proyecto (domain, application, infrastructure)
- [ ] Setup de pytest para testing

**Dependencias principales:**
- FastAPI (REST API)
- boto3 (AWS SDK para DynamoDB, EventBridge, SQS)
- pydantic (validación de datos)
- pytest (testing)

#### Paso 2: Domain Layer - Saga State Machine (2-3 horas) ⏳
- [ ] Definir estados de la Saga:
  - [ ] SagaState enum: STARTED, BOOKING_RESERVED, PAYMENT_PROCESSED, BOOKING_CONFIRMED, COMPLETED, FAILED, COMPENSATING, COMPENSATED
- [ ] Implementar Saga Aggregate:
  - [ ] PaymentSaga (aggregate root)
  - [ ] SagaId (value object)
  - [ ] SagaStep (value object para cada paso)
- [ ] Definir transiciones válidas entre estados
- [ ] Implementar lógica de compensación:
  - [ ] CompensationHandler interface
  - [ ] ReleaseBookingCompensation
  - [ ] RefundPaymentCompensation

**Conceptos clave:**
- State Machine: Controla flujo y transiciones
- Compensation: Rollback distribuido
- Idempotencia: Cada paso puede ejecutarse múltiples veces

#### Paso 3: Domain Layer - Commands y Events (1-2 horas) ⏳
- [ ] Commands:
  - [ ] StartPaymentSagaCommand
  - [ ] ProcessPaymentCommand
  - [ ] ConfirmBookingCommand
  - [ ] CompensateSagaCommand
- [ ] Domain Events:
  - [ ] SagaStarted
  - [ ] PaymentProcessed
  - [ ] PaymentFailed
  - [ ] SagaCompleted
  - [ ] SagaCompensated
- [ ] Ports (interfaces):
  - [ ] SagaRepository (persistencia)
  - [ ] PaymentGateway (mock)
  - [ ] BookingServiceClient (HTTP client)
  - [ ] EventPublisher

#### Paso 4: Application Layer - Saga Orchestrator (2-3 horas) ⏳
- [ ] Implementar SagaOrchestrator:
  - [ ] startSaga(): Inicia flujo de pago
  - [ ] executeStep(): Ejecuta paso individual
  - [ ] compensate(): Ejecuta rollback
  - [ ] handleStepSuccess(): Transición a siguiente paso
  - [ ] handleStepFailure(): Inicia compensación
- [ ] Implementar Step Handlers:
  - [ ] ReserveBookingStepHandler
  - [ ] ProcessPaymentStepHandler
  - [ ] ConfirmBookingStepHandler
  - [ ] SendNotificationStepHandler

**Flujo de orquestación:**
```
START → Reserve Booking → Process Payment → Confirm Booking → Send Notification → COMPLETED
         ↓ (fail)           ↓ (fail)          ↓ (fail)
         COMPENSATE ← COMPENSATE ← COMPENSATE
```

#### Paso 5: Infrastructure - DynamoDB Adapter (1-2 horas) ⏳
- [ ] Configurar tabla de Sagas en DynamoDB:
  - [ ] PK: SAGA#{sagaId}
  - [ ] SK: SAGA#{sagaId}
  - [ ] Attributes: sagaId, status, currentStep, steps[], createdAt, updatedAt
- [ ] Implementar DynamoDBSagaRepository:
  - [ ] save(saga): Persiste estado
  - [ ] findById(sagaId): Recupera saga
  - [ ] updateStatus(sagaId, status): Actualiza estado
- [ ] Implementar SagaMapper (domain ↔ DynamoDB)

#### Paso 6: Infrastructure - External Adapters (2-3 horas) ⏳
- [ ] Mock Payment Gateway:
  - [ ] MockPaymentGateway class
  - [ ] processPayment(): Simula procesamiento (80% éxito, 20% fallo)
  - [ ] refundPayment(): Simula reembolso
- [ ] Booking Service HTTP Client:
  - [ ] BookingServiceClient class
  - [ ] confirmBooking(bookingId): Llama a Booking Service
  - [ ] cancelBooking(bookingId): Llama a Booking Service
- [ ] EventBridge Publisher:
  - [ ] EventBridgePublisher class
  - [ ] publish(event): Publica eventos de saga

#### Paso 7: Infrastructure - Event Consumer (1-2 horas) ⏳
- [ ] Configurar SQS Queue para BookingCreated events
- [ ] Implementar EventBridge Rule: BookingCreated → SQS
- [ ] Implementar SQS Consumer:
  - [ ] Escucha BookingCreated events
  - [ ] Inicia PaymentSaga automáticamente
  - [ ] Maneja reintentos y DLQ

#### Paso 8: Infrastructure - REST API (1-2 horas) ⏳
- [ ] Implementar FastAPI endpoints:
  - [ ] POST /api/v1/payments/saga/start (iniciar saga manualmente)
  - [ ] GET /api/v1/payments/saga/{sagaId} (consultar estado)
  - [ ] POST /api/v1/payments/saga/{sagaId}/compensate (forzar compensación)
- [ ] DTOs:
  - [ ] StartSagaRequest
  - [ ] SagaResponse
- [ ] Error handling y validación

#### Paso 9: Testing (2-3 horas) ⏳
- [ ] Tests unitarios del dominio:
  - [ ] PaymentSaga state transitions
  - [ ] Compensation logic
  - [ ] SagaOrchestrator
- [ ] Tests de integración:
  - [ ] Happy path: Saga completa exitosamente
  - [ ] Failure path: Payment falla, compensación ejecutada
  - [ ] Idempotencia: Reintentos no causan duplicados
- [ ] Mocks para servicios externos

#### Paso 10: Integración con Booking Service (1 hora) ⏳
- [ ] Probar flujo completo:
  - [ ] Crear booking en Booking Service
  - [ ] Payment Service escucha BookingCreated
  - [ ] Saga se ejecuta automáticamente
  - [ ] Booking se confirma o cancela según resultado
- [ ] Verificar datos en DynamoDB (saga state)
- [ ] Verificar eventos en EventBridge

### 📚 Conceptos Clave a Aprender:

**Saga Pattern:**
- Transacciones distribuidas sin 2PC (Two-Phase Commit)
- Cada paso es una transacción local
- Compensación en lugar de rollback tradicional

**Orchestration vs Choreography:**
- Orchestration: Coordinador central (Payment Service)
- Choreography: Servicios reaccionan a eventos (más complejo)

**State Machine:**
- Estados bien definidos
- Transiciones controladas
- Persistencia de estado para recuperación

**Idempotencia:**
- Cada operación puede ejecutarse múltiples veces
- Mismo resultado sin efectos secundarios
- Crítico para reintentos

**Compensation:**
- Rollback semántico (no técnico)
- Orden inverso de ejecución
- Puede fallar (requiere manejo)

### 🎯 Criterios de Éxito:

- [ ] Saga completa flujo happy path correctamente
- [ ] Compensación funciona cuando payment falla
- [ ] Estado de saga persiste en DynamoDB
- [ ] Eventos se publican a EventBridge
- [ ] Tests unitarios >70% cobertura
- [ ] Integración con Booking Service funciona
- [ ] Código sigue principios SOLID
- [ ] Commits siguen Conventional Commits

### 📊 Tiempo Estimado Total: 12-18 horas (1-2 semanas)

---

## ⏳ Fase 4: Notification Service (Buffer Pattern) - PENDIENTE

### Estado: 0% ⏳

### Objetivos:
- [ ] Implementar Buffer Pattern con SQS
- [ ] Configurar Lambda para polling
- [ ] Agregar DLQ para mensajes fallidos
- [ ] Batch processing

---

## ⏳ Fase 5: Integración Final - PENDIENTE

### Estado: 0% ⏳

### Objetivos:
- [ ] Conectar todos los servicios
- [ ] Flujo end-to-end completo
- [ ] Observabilidad con CloudWatch
- [ ] Documentación final

---

## 📈 Progreso General

```
Event Service:        █████████████████░░░  85%
Booking Service:      ████████████████████ 100%
Payment Service:      ░░░░░░░░░░░░░░░░░░░░   0%
Notification Service: ░░░░░░░░░░░░░░░░░░░░   0%
Integration:          ░░░░░░░░░░░░░░░░░░░░   0%
-------------------------------------------
TOTAL:                █████████░░░░░░░░░░░  37%
```

---

## 🎯 Próximo Paso Inmediato

**Iniciar Fase 3: Payment Service (Saga Pattern)**

### Preparación:
1. Revisar plan detallado en sección Fase 3
2. Entender conceptos: Saga Pattern, State Machine, Compensation
3. Verificar Python 3.11+ instalado

### Primer Sprint (Paso 1-2):
1. Setup del proyecto Python/FastAPI
2. Implementar Domain Layer: Saga State Machine
3. Definir estados y transiciones

### Recursos de Aprendizaje:
- Saga Pattern: Chris Richardson - Microservices Patterns
- State Machine: Finite State Machine concepts
- Compensation: Distributed transactions patterns

**Después de Fase 3:**
- Fase 4: Notification Service (Buffer Pattern)
- Fase 5: Integración completa end-to-end

---

## 📝 Notas

- Cada fase se puede completar de forma independiente
- Es válido volver a fases anteriores para mejorar
- El objetivo es aprender los patrones, no perfeccionar cada servicio
- Mantener commits profesionales con Conventional Commits
