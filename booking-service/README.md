# Booking Service - CQRS + Hexagonal Architecture

Microservicio de gestión de reservas con DynamoDB en LocalStack.

## 🎯 Patrones Arquitectónicos

- **Hexagonal Architecture:** Separación de dominio, aplicación e infraestructura
- **CQRS:** Separación de Commands (write) y Queries (read)
- **Event-Driven Architecture:** Comunicación asíncrona con EventBridge

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│              Infrastructure Layer                   │
│  ┌──────────┐  ┌─────────────┐  ┌───────────────┐ │
│  │ REST API │  │  DynamoDB   │  │  EventBridge  │ │
│  │  (IN)    │  │  Write+Read │  │     (OUT)     │ │
│  └────┬─────┘  └──────┬──────┘  └───────┬───────┘ │
│       │               │                  │         │
│  ┌────▼───────────────▼──────────────────▼───────┐ │
│  │         Application Layer (CQRS)              │ │
│  │  Command Handlers  |  Query Handlers          │ │
│  └────┬──────────────────────────────────────────┘ │
│       │                                            │
│  ┌────▼──────────────────────────────────────────┐ │
│  │            Domain Layer                       │ │
│  │  Booking, Commands, Queries, Events           │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 📦 Componentes

### Domain Layer
- **Aggregates:** Booking
- **Value Objects:** BookingId, UserId, EventId, BookingStatus, TicketQuantity, TotalPrice
- **Commands:** CreateBookingCommand, ConfirmBookingCommand, CancelBookingCommand
- **Queries:** GetBookingByIdQuery, GetBookingsByUserQuery, GetBookingsByEventQuery
- **Domain Events:** BookingCreated, BookingConfirmed, BookingCancelled
- **Ports:** BookingRepository (write), BookingQueryRepository (read), EventPublisher

### Application Layer
- **Command Handlers:** CreateBookingHandler, ConfirmBookingHandler, CancelBookingHandler
- **Query Handlers:** GetBookingByIdHandler, GetBookingsByUserHandler, GetBookingsByEventHandler

### Infrastructure Layer
- **DynamoDB Adapters:** Write Model, Read Model con GSI
- **EventBridge Adapter:** Publisher y Consumer
- **REST API:** Express controllers

## 🚀 Inicio Rápido

### Prerequisitos
- Node.js 20+
- LocalStack corriendo
- DynamoDB configurado

### Instalación

```bash
cd booking-service
npm install
```

### Desarrollo

```bash
npm run dev
```

### Tests

```bash
npm test
```

## 🔄 CQRS Implementation

### Write Model (Commands)
- Optimizado para validaciones y reglas de negocio
- Garantiza consistencia transaccional
- Publica eventos de dominio

### Read Model (Queries)
- Optimizado para consultas rápidas
- Usa GSI de DynamoDB para búsquedas eficientes
- Eventual consistency con Write Model

### Sincronización
Los modelos se sincronizan mediante eventos de dominio:
1. Command Handler crea/actualiza Booking
2. Publica evento (BookingCreated, BookingConfirmed, etc.)
3. Event Handler actualiza Read Model

## 📊 DynamoDB Schema

### Tabla: Bookings

**Primary Key:**
- PK: `BOOKING#{bookingId}`
- SK: `BOOKING#{bookingId}`

**GSI 1: UserBookingsIndex**
- PK: `USER#{userId}`
- SK: `BOOKING#{createdAt}`

**GSI 2: EventBookingsIndex**
- PK: `EVENT#{eventId}`
- SK: `BOOKING#{createdAt}`

**Attributes:**
- bookingId (string)
- userId (string)
- eventId (string)
- status (PENDING | CONFIRMED | CANCELLED)
- ticketQuantity (number)
- totalPrice (number)
- createdAt (string ISO)
- updatedAt (string ISO)

## 🧪 Testing

### 1. Inicializar LocalStack y DynamoDB

```bash
# Iniciar LocalStack
docker-compose up -d

# Crear tabla de DynamoDB con GSI
bash init-dynamodb.sh
```

### 2. Iniciar el servicio

```bash
cd booking-service
npm install
npm run dev
```

### 3. Probar endpoints

```bash
# Health check
curl http://localhost:3001/health

# Crear una reserva
curl -X POST http://localhost:3001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "eventId": "660e8400-e29b-41d4-a716-446655440000",
    "ticketQuantity": 2,
    "pricePerTicket": 50.00
  }'

# Obtener reserva por ID
curl http://localhost:3001/api/v1/bookings/{bookingId}

# Confirmar reserva
curl -X POST http://localhost:3001/api/v1/bookings/{bookingId}/confirm

# Cancelar reserva
curl -X POST http://localhost:3001/api/v1/bookings/{bookingId}/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason": "User requested cancellation"}'

# Obtener reservas por usuario
curl http://localhost:3001/api/v1/bookings/user/{userId}

# Obtener reservas por evento
curl http://localhost:3001/api/v1/bookings/event/{eventId}
```

### 4. Verificar datos en DynamoDB

```bash
# Ver todas las reservas
awslocal dynamodb scan --table-name Bookings

# Ver reservas de un usuario (usando GSI)
awslocal dynamodb query \
  --table-name Bookings \
  --index-name UserBookingsIndex \
  --key-condition-expression "userId = :userId" \
  --expression-attribute-values '{":userId":{"S":"550e8400-e29b-41d4-a716-446655440000"}}'
```

## ✅ Estado Actual

- [x] Domain Layer (100%)
- [x] Application Layer (100%)
- [x] Infrastructure Layer (100%)
- [x] REST API (100%)
- [x] Tests unitarios (41 tests passing)
- [ ] Tests de integración
- [ ] Integración con Event Service

## 📚 Conceptos Clave

**CQRS:** Separación de responsabilidades entre escritura y lectura
**Eventual Consistency:** Los modelos se sincronizan mediante eventos
**GSI:** Índices secundarios para queries eficientes en DynamoDB
