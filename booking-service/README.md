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

## 🎯 Próximos Pasos

- [ ] Implementar Domain Layer
- [ ] Implementar Application Layer (CQRS)
- [ ] Configurar DynamoDB con GSI
- [ ] Implementar REST API
- [ ] Tests unitarios
- [ ] Integración con Event Service

## 📚 Conceptos Clave

**CQRS:** Separación de responsabilidades entre escritura y lectura
**Eventual Consistency:** Los modelos se sincronizan mediante eventos
**GSI:** Índices secundarios para queries eficientes en DynamoDB
