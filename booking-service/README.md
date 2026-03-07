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
- LocalStack corriendo (con `docker-compose up -d` en la raíz del proyecto)
- DynamoDB configurado (tabla `Bookings` creada)

### Instalación

```powershell
cd booking-service
npm install
```

### Desarrollo

```powershell
npm run dev
```

### Tests

```powershell
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
- PK: `userId` (string, UUID plano)
- SK: `createdAt` (string ISO)

**GSI 2: EventBookingsIndex**
- PK: `eventId` (string, UUID plano)
- SK: `createdAt` (string ISO)

**Attributes:**
- bookingId (string)
- userId (string)
- eventId (string)
- status (PENDING | CONFIRMED | CANCELLED)
- ticketQuantity (number)
- totalPrice (number)
- createdAt (string ISO)
- updatedAt (string ISO)

## 🧪 Testing (Git Bash)

> ⚠️ Todos los comandos de esta sección son para **Git Bash** en Windows.
> Abre Git Bash y ubícate en la raíz del proyecto antes de empezar.

### Paso 1 — Iniciar LocalStack

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Esperar a que esté healthy (~10 segundos) y verificar:
curl -s http://localhost:4566/_localstack/health | grep dynamodb
# Debe mostrar: "dynamodb": "available"
```

### Paso 2 — Crear tabla DynamoDB

```bash
# Desde la raíz del proyecto
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

bash init-dynamodb.sh
```

> Si la tabla ya existe, verás el error `Table already exists: Bookings` — eso está bien, significa que ya fue creada antes y los datos persisten.

### Paso 3 — Instalar dependencias e iniciar el servicio

```bash
cd booking-service
npm install
npm run dev
```

> Cuando veas `Server listening on port 3001`, el servicio está listo.

### Paso 4 — Probar endpoints

Abre **otra pestaña de Git Bash** (deja el servicio corriendo) y ejecuta:

```bash
# Health check — debe responder {"status":"healthy"}
curl http://localhost:3001/health

# Crear una reserva
curl -s -X POST http://localhost:3001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{"userId":"550e8400-e29b-41d4-a716-446655440000","eventId":"660e8400-e29b-41d4-a716-446655440000","ticketQuantity":2,"pricePerTicket":50.00}'
```

> Guarda el `id` que aparece en la respuesta, lo necesitas para los siguientes comandos.
> Reemplaza `{bookingId}` con ese ID en los comandos de abajo.

```bash
# Obtener reserva por ID
curl http://localhost:3001/api/v1/bookings/{bookingId}

# Confirmar reserva
curl -X POST http://localhost:3001/api/v1/bookings/{bookingId}/confirm

# Cancelar reserva
curl -X POST http://localhost:3001/api/v1/bookings/{bookingId}/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason":"User requested cancellation"}'

# Obtener todas las reservas de un usuario
curl http://localhost:3001/api/v1/bookings/user/550e8400-e29b-41d4-a716-446655440000

# Obtener todas las reservas de un evento
curl http://localhost:3001/api/v1/bookings/event/660e8400-e29b-41d4-a716-446655440000
```

### Paso 5 — Verificar datos en DynamoDB (opcional)

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Ver todas las reservas guardadas
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name Bookings
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
