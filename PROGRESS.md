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

## 🚀 Fase 2: Booking Service (CQRS + Hexagonal) - EN PROGRESO

### Estado: 30% ⏳

### Objetivos de Aprendizaje:
- [ ] Implementar CQRS (Command Query Responsibility Segregation)
- [ ] Usar DynamoDB con índices GSI
- [ ] Separar Write Model y Read Model
- [ ] Eventual Consistency entre modelos
- [ ] Consumir eventos de EventBridge

### Plan de Implementación:

#### Paso 1: Setup del Proyecto (30 min) ✅
- [x] Crear estructura de carpetas para Booking Service (TypeScript/Node.js)
- [x] Configurar package.json con dependencias
- [x] Configurar TypeScript (tsconfig.json)
- [x] Crear estructura Hexagonal (domain, application, infrastructure)

#### Paso 2: Domain Layer (1-2 horas) ✅
- [x] Implementar Value Objects:
  - [x] BookingId
  - [x] UserId
  - [x] EventId
  - [x] BookingStatus (PENDING, CONFIRMED, CANCELLED)
  - [x] TicketQuantity
  - [x] TotalPrice
- [x] Implementar Booking Aggregate:
  - [x] Booking.create() (factory method)
  - [x] Booking.confirm() (state transition)
  - [x] Booking.cancel() (state transition)
- [x] Implementar Domain Events:
  - [x] BookingCreated
  - [x] BookingConfirmed
  - [x] BookingCancelled
- [x] Definir Ports:
  - [x] BookingRepository (write)
  - [x] BookingQueryRepository (read)
  - [x] EventPublisher

#### Paso 3: Application Layer - CQRS (2-3 horas)
- [ ] Commands (Write Side):
  - [ ] CreateBookingCommand
  - [ ] ConfirmBookingCommand
  - [ ] CancelBookingCommand
- [ ] Command Handlers:
  - [ ] CreateBookingHandler
  - [ ] ConfirmBookingHandler
  - [ ] CancelBookingHandler
- [ ] Queries (Read Side):
  - [ ] GetBookingByIdQuery
  - [ ] GetBookingsByUserQuery
  - [ ] GetBookingsByEventQuery
- [ ] Query Handlers:
  - [ ] GetBookingByIdHandler
  - [ ] GetBookingsByUserHandler
  - [ ] GetBookingsByEventHandler

#### Paso 4: Infrastructure - DynamoDB (2-3 horas)
- [ ] Configurar DynamoDB en LocalStack
- [ ] Crear tabla de Bookings con GSI
- [ ] Implementar Write Model Adapter:
  - [ ] DynamoDBBookingRepository
  - [ ] BookingMapper (domain ↔ DynamoDB)
- [ ] Implementar Read Model Adapter:
  - [ ] DynamoDBBookingQueryRepository
  - [ ] Queries optimizadas con GSI

#### Paso 5: Infrastructure - EventBridge (1 hora)
- [ ] Implementar EventBridge Publisher Adapter
- [ ] Implementar EventBridge Consumer:
  - [ ] Escuchar EventPublished del Event Service
  - [ ] Crear índice de disponibilidad

#### Paso 6: Infrastructure - REST API (1 hora)
- [ ] Implementar REST Controllers:
  - [ ] POST /api/v1/bookings (crear reserva)
  - [ ] POST /api/v1/bookings/{id}/confirm (confirmar)
  - [ ] POST /api/v1/bookings/{id}/cancel (cancelar)
  - [ ] GET /api/v1/bookings/{id} (detalles)
  - [ ] GET /api/v1/bookings/user/{userId} (por usuario)
  - [ ] GET /api/v1/bookings/event/{eventId} (por evento)

#### Paso 7: Tests (1-2 horas)
- [ ] Tests unitarios del dominio
- [ ] Tests de Command Handlers
- [ ] Tests de Query Handlers
- [ ] Tests de integración con DynamoDB

#### Paso 8: Integración con Event Service (30 min)
- [ ] Probar flujo completo:
  - [ ] Event Service publica EventPublished
  - [ ] Booking Service lo consume
  - [ ] Crear reserva en Booking Service
  - [ ] Verificar datos en DynamoDB

### 📚 Conceptos Clave a Aprender:
- **CQRS:** Separación de responsabilidades entre escritura y lectura
- **Write Model:** Optimizado para validaciones y consistencia
- **Read Model:** Optimizado para consultas rápidas
- **Eventual Consistency:** Los modelos se sincronizan mediante eventos
- **DynamoDB GSI:** Índices secundarios para queries eficientes

---

## ⏳ Fase 3: Payment Service (Saga Pattern) - PENDIENTE

### Estado: 0% ⏳

### Objetivos:
- [ ] Implementar Saga Pattern con orchestration
- [ ] Crear state machine para flujo de pago
- [ ] Implementar compensación para fallos
- [ ] Coordinar múltiples servicios

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
Booking Service:      ░░░░░░░░░░░░░░░░░░░░   0%
Payment Service:      ░░░░░░░░░░░░░░░░░░░░   0%
Notification Service: ░░░░░░░░░░░░░░░░░░░░   0%
Integration:          ░░░░░░░░░░░░░░░░░░░░   0%
-------------------------------------------
TOTAL:                ████░░░░░░░░░░░░░░░░  17%
```

---

## 🎯 Próximo Paso Inmediato

**Iniciar Fase 2: Booking Service**

1. Crear estructura del proyecto TypeScript
2. Implementar Domain Layer con CQRS
3. Configurar DynamoDB en LocalStack

---

## 📝 Notas

- Cada fase se puede completar de forma independiente
- Es válido volver a fases anteriores para mejorar
- El objetivo es aprender los patrones, no perfeccionar cada servicio
- Mantener commits profesionales con Conventional Commits
