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

### Plan de Implementación:

#### Paso 1: Setup del Proyecto (30-45 min) ⏳
- [ ] Crear estructura de carpetas para Payment Service (Python/FastAPI)
- [ ] Crear y activar virtual environment (venv)
- [ ] Configurar requirements.txt con dependencias
- [ ] Configurar pyproject.toml (opcional, para gestión moderna)
- [ ] Crear .gitignore para Python (venv/, __pycache__, .pytest_cache, etc.)
- [ ] Configurar estructura de proyecto (src/domain, src/application, src/infrastructure)
- [ ] Setup de pytest para testing
- [ ] Crear README.md con instrucciones de setup

**Dependencias principales:**
- FastAPI (REST API)
- uvicorn (ASGI server)
- boto3 (AWS SDK para DynamoDB, EventBridge, SQS)
- pydantic (validación de datos)
- pytest (testing)
- pytest-cov (cobertura de tests)
- httpx (HTTP client para testing)
- python-dotenv (variables de entorno)

**Estructura de carpetas:**
```
payment-service/
├── venv/                    # Virtual environment (no commitear)
├── src/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── saga/
│   │   └── compensation/
│   ├── application/
│   │   └── __init__.py
│   └── infrastructure/
│       ├── __init__.py
│       ├── persistence/
│       ├── messaging/
│       └── api/
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
├── README.md
└── main.py
```

**Buenas prácticas incluidas:**
- ✅ Virtual environment para aislamiento de dependencias
- ✅ .gitignore para no commitear archivos innecesarios
- ✅ .env.example para documentar variables de entorno
- ✅ Estructura clara de carpetas (domain, application, infrastructure)
- ✅ Tests separados por tipo (unit, integration)
- ✅ requirements.txt con versiones específicas

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
