# Payment Service - Saga Pattern (Orchestration)

Microservicio de procesamiento de pagos con patrón Saga para transacciones distribuidas.

## 🎯 Patrón Arquitectónico: Saga Pattern

El Saga Pattern es un patrón para manejar transacciones distribuidas sin usar 2PC (Two-Phase Commit). En lugar de una transacción ACID tradicional, una saga es una secuencia de transacciones locales donde cada paso publica eventos y/o ejecuta comandos.

### ¿Por qué Saga Pattern?

**Problema:**
En sistemas distribuidos, no podemos usar transacciones ACID tradicionales que abarquen múltiples servicios. Si el pago se procesa pero la confirmación de booking falla, ¿cómo revertimos el pago?

**Solución:**
Saga Pattern coordina múltiples transacciones locales y proporciona compensación en caso de fallo.

### Orchestration vs Choreography

Este servicio usa **Orchestration** (coordinador central):

**Orchestration (usado aquí):**
- ✅ Coordinador central (Payment Service)
- ✅ Flujo explícito y fácil de entender
- ✅ Más fácil de debuggear
- ❌ Acoplamiento al orquestador

**Choreography (alternativa):**
- ✅ Sin coordinador central
- ✅ Servicios reaccionan a eventos
- ❌ Flujo implícito, más difícil de seguir
- ❌ Más complejo de implementar

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Payment Service                          │
│                  (Saga Orchestrator)                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Domain Layer                            │  │
│  │  ┌────────────────┐  ┌──────────────────────────┐   │  │
│  │  │  PaymentSaga   │  │  Compensation Handlers   │   │  │
│  │  │ (State Machine)│  │  - ReleaseBooking        │   │  │
│  │  │                │  │  - RefundPayment         │   │  │
│  │  └────────────────┘  └──────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Application Layer                          │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │         Saga Orchestrator                      │  │  │
│  │  │  - startSaga()                                 │  │  │
│  │  │  - executeStep()                               │  │  │
│  │  │  - compensate()                                │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Infrastructure Layer                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐   │  │
│  │  │ DynamoDB │  │EventBridge│  │ Booking Service │   │  │
│  │  │(Saga State)│  │  + SQS   │  │   HTTP Client   │   │  │
│  │  └──────────┘  └──────────┘  └─────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Saga Flow

### Happy Path (Éxito)

```
1. START
   ↓
2. Reserve Booking (Booking Service)
   ↓
3. Process Payment (Payment Gateway)
   ↓
4. Confirm Booking (Booking Service)
   ↓
5. Send Notification (Notification Service)
   ↓
6. COMPLETED
```

### Failure Path (Compensación)

```
1. START
   ↓
2. Reserve Booking ✓
   ↓
3. Process Payment ✗ (FALLO)
   ↓
4. COMPENSATE
   ↓
5. Release Booking (compensación)
   ↓
6. COMPENSATED
```

## 📊 State Machine

### Estados de la Saga

```python
class SagaState(Enum):
    STARTED = "STARTED"                    # Saga iniciada
    BOOKING_RESERVED = "BOOKING_RESERVED"  # Booking reservado
    PAYMENT_PROCESSED = "PAYMENT_PROCESSED" # Pago procesado
    BOOKING_CONFIRMED = "BOOKING_CONFIRMED" # Booking confirmado
    COMPLETED = "COMPLETED"                # Saga completada
    FAILED = "FAILED"                      # Saga falló
    COMPENSATING = "COMPENSATING"          # Ejecutando compensación
    COMPENSATED = "COMPENSATED"            # Compensación completada
```

### Transiciones Válidas

```
STARTED → BOOKING_RESERVED → PAYMENT_PROCESSED → BOOKING_CONFIRMED → COMPLETED
   ↓            ↓                    ↓                    ↓
FAILED      COMPENSATING        COMPENSATING         COMPENSATING
               ↓                    ↓                    ↓
           COMPENSATED          COMPENSATED          COMPENSATED
```

## 🔑 Conceptos Clave

### 1. Idempotencia

Cada operación debe ser idempotente (puede ejecutarse múltiples veces con el mismo resultado):

```python
# ✅ Idempotente
def process_payment(payment_id, amount):
    if payment_exists(payment_id):
        return get_payment(payment_id)  # Ya procesado
    return create_payment(payment_id, amount)

# ❌ No idempotente
def process_payment(amount):
    return create_payment(amount)  # Crea duplicados en reintentos
```

### 2. Compensación

La compensación es un "rollback semántico", no técnico:

```python
# Operación normal
def reserve_booking(booking_id):
    booking.status = "RESERVED"
    save(booking)

# Compensación (rollback semántico)
def release_booking(booking_id):
    booking.status = "CANCELLED"
    save(booking)
```

### 3. Persistencia de Estado

El estado de la saga se persiste en cada paso para recuperación:

```python
# Antes de cada paso
saga.current_step = "PROCESS_PAYMENT"
saga_repository.save(saga)

# Ejecutar paso
result = payment_gateway.process(amount)

# Después del paso
saga.status = "PAYMENT_PROCESSED"
saga_repository.save(saga)
```

## 📦 Componentes

### Domain Layer
- **PaymentSaga:** Aggregate root con state machine
- **SagaStep:** Value object para cada paso
- **CompensationHandler:** Interface para compensaciones
- **Domain Events:** SagaStarted, PaymentProcessed, SagaCompleted, etc.

### Application Layer
- **SagaOrchestrator:** Coordina ejecución de pasos
- **Step Handlers:** Lógica de cada paso individual

### Infrastructure Layer
- **DynamoDBSagaRepository:** Persiste estado de saga
- **MockPaymentGateway:** Simula procesamiento de pagos
- **BookingServiceClient:** Cliente HTTP para Booking Service
- **EventBridgePublisher:** Publica eventos de saga
- **SQSConsumer:** Escucha eventos BookingCreated

## 🚀 Inicio Rápido

### Prerequisitos
- Python 3.11+
- LocalStack corriendo
- Booking Service corriendo
- DynamoDB configurado

### Instalación

```bash
cd payment-service
pip install -r requirements.txt
```

### Desarrollo

```bash
uvicorn main:app --reload --port 3002
```

### Tests

```bash
pytest
pytest --cov=src  # Con cobertura
```

## 🧪 Testing

### Probar Happy Path

```bash
# 1. Crear booking en Booking Service
curl -X POST http://localhost:3001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "eventId": "660e8400-e29b-41d4-a716-446655440000",
    "ticketQuantity": 2,
    "pricePerTicket": 50.00
  }'

# 2. Payment Service escucha BookingCreated y inicia saga automáticamente

# 3. Consultar estado de saga
curl http://localhost:3002/api/v1/payments/saga/{sagaId}
```

### Probar Failure Path

```bash
# Forzar fallo en payment gateway (configuración)
# La saga ejecutará compensación automáticamente
```

## 📚 Recursos de Aprendizaje

### Saga Pattern
- [Microservices Patterns - Chris Richardson](https://microservices.io/patterns/data/saga.html)
- [Saga Pattern Explained](https://blog.couchbase.com/saga-pattern-implement-business-transactions-using-microservices-part/)

### State Machine
- [Finite State Machine](https://en.wikipedia.org/wiki/Finite-state_machine)
- [State Pattern](https://refactoring.guru/design-patterns/state)

### Distributed Transactions
- [Distributed Transactions: The Icebergs of Microservices](https://www.grahamlea.com/2016/08/distributed-transactions-microservices-icebergs/)

## 🎯 Próximos Pasos

- [ ] Implementar Domain Layer
- [ ] Implementar Application Layer (Orchestrator)
- [ ] Configurar DynamoDB para saga state
- [ ] Implementar adapters (Payment Gateway, Booking Client)
- [ ] Tests unitarios
- [ ] Integración con Booking Service

## 📝 Notas de Diseño

### ¿Por qué DynamoDB para Saga State?

- **Transacciones locales:** Cada actualización de estado es atómica
- **Consultas rápidas:** Recuperar estado de saga por ID
- **Escalabilidad:** Maneja alto volumen de sagas concurrentes
- **TTL:** Limpiar sagas antiguas automáticamente

### ¿Por qué Mock Payment Gateway?

Para este proyecto educativo, simulamos el payment gateway. En producción:
- Stripe, PayPal, Adyen, etc.
- Webhooks para confirmación asíncrona
- Manejo de 3D Secure, PCI compliance
- Reintentos y circuit breakers

### Manejo de Errores

- **Reintentos:** Exponential backoff para fallos transitorios
- **DLQ:** Dead Letter Queue para fallos permanentes
- **Alertas:** CloudWatch alarms para sagas atascadas
- **Timeout:** Sagas que no completan en X tiempo
