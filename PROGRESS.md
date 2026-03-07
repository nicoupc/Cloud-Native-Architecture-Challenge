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

## 🚀 Fase 3: Payment Service (Saga Pattern) - COMPLETADA

### Estado: 100% ✅

### Objetivos de Aprendizaje:
- [x] Implementar Saga Pattern con orchestration
- [x] Crear state machine para flujo de pago distribuido
- [x] Implementar compensación automática en caso de fallos
- [x] Coordinar múltiples servicios (Booking, Payment Gateway, Notification)
- [x] Manejar idempotencia y reintentos
- [x] Persistir estado de saga en DynamoDB

### Implementación Completada:

#### ✅ Domain Layer (100%)
- [x] SagaState: 8 estados con transiciones válidas
- [x] Value Objects: SagaId, BookingId, Amount, SagaStep
- [x] PaymentSaga: Aggregate root con 4 pasos predefinidos
- [x] Domain Events: 9 eventos inmutables (SagaStarted, PaymentProcessed, etc.)
- [x] Ports: 5 interfaces (SagaRepository, EventPublisher, PaymentGateway, etc.)
- [x] Domain Exceptions: SagaNotFoundException, InvalidStateTransitionException
- [x] Tests: 70+ unit tests con 100% cobertura

#### ✅ Application Layer (100%)
- [x] SagaOrchestrator: Coordinador central con retry y compensación
- [x] 4 Saga Steps: RESERVE_BOOKING, PROCESS_PAYMENT, CONFIRM_BOOKING, SEND_NOTIFICATION
- [x] Retry logic: Máximo 3 intentos por paso
- [x] Compensation: Rollback en orden inverso
- [x] Event publishing: Eventos en cada transición
- [x] Tests: 70+ unit tests con mocks

#### ✅ Infrastructure Layer (100%)
- [x] DynamoDBSagaRepository: Persistencia con GSI para queries
- [x] SagaMapper: Traducción domain ↔ DynamoDB
- [x] EventBridgePublisher: Publicación de eventos
- [x] MockPaymentGateway: Simulador con 80% success rate
- [x] HttpBookingServiceClient: Cliente HTTP para Booking Service
- [x] EventBridgeNotificationClient: Cliente para notificaciones

#### ✅ REST API (100%)
- [x] FastAPI application con dependency injection
- [x] 4 endpoints: POST /sagas, GET /sagas/{id}, GET /sagas, POST /sagas/{id}/compensate
- [x] DTOs: Request/Response models con Pydantic
- [x] Error handling: HTTP status codes apropiados
- [x] Health check endpoint
- [x] CORS configurado

#### ✅ Scripts y Configuración (100%)
- [x] init-dynamodb.sh: Script para crear tabla con GSI
- [x] requirements.txt: Dependencias con versiones específicas
- [x] .env.example: Variables de entorno documentadas
- [x] pytest.ini: Configuración de tests con 70% cobertura
- [x] README.md: Documentación completa con Saga Pattern

### 📚 Conceptos Aprendidos:
- ✅ Saga Pattern: Transacciones distribuidas sin 2PC
- ✅ Orchestration: Coordinador central vs Choreography
- ✅ State Machine: Estados y transiciones controladas
- ✅ Compensation: Rollback semántico (no técnico)
- ✅ Idempotencia: Operaciones repetibles sin efectos secundarios
- ✅ Hexagonal Architecture: Ports & Adapters en Python
- ✅ Event-Driven: Publicación de eventos de dominio
- ✅ Dependency Injection: DI manual con FastAPI

### 🎯 Próximos Pasos (Opcionales):
- [ ] Tests de integración con LocalStack
- [ ] SQS Consumer para BookingCreated events
- [ ] Integración end-to-end con Booking Service
- [ ] Métricas y observabilidad

---

## ⏳ Fase 4: Notification Service (Buffer Pattern) - EN PROGRESO

### Estado: 5% ⏳

### Objetivos de Aprendizaje:
- [ ] Implementar Buffer Pattern con SQS
- [ ] Long polling para consumo eficiente de mensajes
- [ ] Configurar Dead Letter Queue (DLQ) para mensajes fallidos
- [ ] Batch processing de notificaciones
- [ ] Mock email provider para simulación
- [ ] Manejo de reintentos y visibility timeout

### Plan de Implementación:

#### Paso 1: Setup del Proyecto (30 min) ✅
- [x] Crear estructura de carpetas (domain, application, infrastructure)
- [x] Configurar requirements.txt con dependencias
- [x] Crear .gitignore para Python
- [x] Configurar pytest para testing
- [x] Crear README.md con Buffer Pattern explicado
- [x] .env.example con configuración de SQS

#### Paso 2: Domain Layer (1-2 horas) ⏳
- [ ] Notification Aggregate:
  - [ ] NotificationId (value object)
  - [ ] NotificationType enum (BOOKING_CONFIRMED, PAYMENT_PROCESSED, etc.)
  - [ ] Notification aggregate con estado
- [ ] Email Templates:
  - [ ] BookingConfirmedTemplate
  - [ ] PaymentProcessedTemplate
  - [ ] PaymentFailedTemplate
- [ ] Domain Events:
  - [ ] NotificationSent
  - [ ] NotificationFailed
- [ ] Ports:
  - [ ] EmailProvider (interface)
  - [ ] NotificationRepository (opcional, para tracking)

#### Paso 3: Application Layer (1-2 horas) ⏳
- [ ] NotificationProcessor:
  - [ ] processMessage(): Procesa mensaje de SQS
  - [ ] sendEmail(): Envía email usando provider
  - [ ] handleFailure(): Maneja fallos y reintentos
- [ ] MessageHandler:
  - [ ] Parsea diferentes tipos de mensajes
  - [ ] Valida estructura de mensajes
  - [ ] Extrae datos para templates

#### Paso 4: Infrastructure - SQS Consumer (2-3 horas) ⏳
- [ ] SQSConsumer:
  - [ ] Long polling (WaitTimeSeconds=20)
  - [ ] Batch receive (MaxNumberOfMessages=10)
  - [ ] Visibility timeout management
  - [ ] Delete messages after processing
  - [ ] Error handling y logging
- [ ] Message Parser:
  - [ ] Parse EventBridge events
  - [ ] Extract notification data
  - [ ] Validate message structure

#### Paso 5: Infrastructure - Mock Email Provider (1 hora) ⏳
- [ ] MockEmailProvider:
  - [ ] sendEmail(): Simula envío (logs)
  - [ ] Configurable success rate
  - [ ] Delay simulation
  - [ ] Email tracking (in-memory)

#### Paso 6: Infrastructure - SQS Setup Script (30 min) ⏳
- [ ] init-sqs.sh:
  - [ ] Crear notification-queue
  - [ ] Crear notification-dlq
  - [ ] Configurar redrive policy (maxReceiveCount=3)
  - [ ] Configurar visibility timeout
  - [ ] Configurar message retention

#### Paso 7: Infrastructure - EventBridge Integration (1 hora) ⏳
- [ ] EventBridge Rules:
  - [ ] Rule: BookingConfirmed → SQS
  - [ ] Rule: PaymentProcessed → SQS
  - [ ] Rule: PaymentFailed → SQS
- [ ] Script para crear rules

#### Paso 8: Main Application (1 hora) ⏳
- [ ] Consumer Loop:
  - [ ] Infinite loop con long polling
  - [ ] Graceful shutdown (SIGTERM)
  - [ ] Health check endpoint (opcional)
  - [ ] Metrics logging

#### Paso 9: Testing (2-3 horas) ⏳
- [ ] Unit Tests:
  - [ ] Notification domain tests
  - [ ] Email template tests
  - [ ] Message parser tests
- [ ] Integration Tests:
  - [ ] SQS consumer tests con LocalStack
  - [ ] End-to-end message flow
  - [ ] DLQ behavior tests

#### Paso 10: Integration Testing (1 hora) ⏳
- [ ] Probar flujo completo:
  - [ ] Publicar evento a EventBridge
  - [ ] Verificar mensaje en SQS
  - [ ] Consumer procesa mensaje
  - [ ] Email "enviado" (logged)
  - [ ] Mensaje eliminado de cola

### 📚 Conceptos Clave a Aprender:

**Buffer Pattern:**
- Desacoplamiento entre productores y consumidores
- Cola intermedia para absorber picos de carga
- Procesamiento asíncrono

**Long Polling:**
- Reduce llamadas a SQS (costo)
- Reduce latencia vs short polling
- WaitTimeSeconds hasta 20 segundos

**Visibility Timeout:**
- Previene procesamiento duplicado
- Mensaje invisible mientras se procesa
- Vuelve a estar disponible si no se elimina

**Dead Letter Queue:**
- Almacena mensajes que fallan repetidamente
- Permite análisis y corrección manual
- Previene pérdida de mensajes

**Batch Processing:**
- Procesa múltiples mensajes a la vez
- Más eficiente que uno por uno
- Reduce llamadas a SQS

### 🎯 Criterios de Éxito:

- [ ] Consumer procesa mensajes de SQS correctamente
- [ ] Long polling funciona (espera hasta 20s)
- [ ] Mensajes fallidos van a DLQ después de 3 intentos
- [ ] Mock email provider simula envíos
- [ ] Tests unitarios >70% cobertura
- [ ] Integración con EventBridge funciona
- [ ] Código sigue principios SOLID
- [ ] Commits siguen Conventional Commits

### 📊 Tiempo Estimado Total: 8-12 horas (1 semana)

---## ⏳ Fase 5: Integración Final - PENDIENTE

### Estado: 0% ⏳

### Objetivos:
- [ ] Conectar todos los servicios end-to-end
- [ ] Flujo completo: Event → Booking → Payment → Notification
- [ ] Probar happy path y failure paths
- [ ] Observabilidad con CloudWatch (opcional)
- [ ] Documentación final del proyecto

---

## 📈 Progreso General

```
Event Service:        █████████████████░░░  85%
Booking Service:      ████████████████████ 100%
Payment Service:      ████████████████████ 100%
Notification Service: ░░░░░░░░░░░░░░░░░░░░   0%
Integration:          ░░░░░░░░░░░░░░░░░░░░   0%
-------------------------------------------
TOTAL:                ██████████████░░░░░░  57%
```

---

## 🎯 Próximo Paso Inmediato

**Iniciar Fase 4: Notification Service (Buffer Pattern)**

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
