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
- Python 3.11+ instalado
- LocalStack corriendo (`docker-compose up -d`)
- Booking Service corriendo (puerto 3001)
- DynamoDB configurado

### Instalación Profesional

```bash
# 1. Navegar al directorio del servicio
cd payment-service

# 2. Crear virtual environment (aislamiento de dependencias)
python -m venv venv

# 3. Activar virtual environment (Git Bash en Windows)
source venv/Scripts/activate

# 4. Verificar que estás en el virtual environment
# Deberías ver (venv) en tu prompt
which python  # Debe apuntar a venv/Scripts/python

# 5. Actualizar pip (buena práctica)
pip install --upgrade pip

# 6. Instalar dependencias con versiones específicas
pip install -r requirements.txt

# 7. Copiar configuración de ejemplo
cp .env.example .env

# 8. Editar .env si es necesario (opcional para desarrollo local)
# nano .env
```

### Verificar Instalación

```bash
# Verificar que FastAPI está instalado
python -c "import fastapi; print(fastapi.__version__)"

# Verificar que boto3 está instalado
python -c "import boto3; print(boto3.__version__)"

# Listar todas las dependencias instaladas
pip list
```

### Desarrollo

```bash
# Asegúrate de tener el virtual environment activado (ver (venv) en prompt)
uvicorn src.main:app --reload --port 3002 --host 0.0.0.0

# O usando Python directamente
python -m src.main
```

### Desactivar Virtual Environment

```bash
# Cuando termines de trabajar
deactivate
```

### Estructura del Proyecto

```
payment-service/
├── venv/                    # Virtual environment (NO commitear)
├── src/
│   ├── domain/              # Lógica de negocio pura
│   ├── application/         # Casos de uso
│   └── infrastructure/      # Adaptadores externos
├── tests/
│   ├── unit/                # Tests unitarios (rápidos)
│   └── integration/         # Tests de integración (LocalStack)
├── .env                     # Variables de entorno (NO commitear)
├── .env.example             # Plantilla de configuración
├── .gitignore               # Archivos a ignorar en git
├── requirements.txt         # Dependencias con versiones
├── pytest.ini               # Configuración de tests
├── README.md                # Esta documentación
└── main.py                  # Punto de entrada
```

### Tests

```bash
pytest
pytest --cov=src  # Con cobertura
```

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
cd payment-service
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

bash scripts/init-dynamodb.sh
```

> Si la tabla ya existe, verás `Table payment-sagas already exists` — eso está bien, significa que ya fue creada antes y los datos persisten.

### Paso 3 — Activar virtual environment e instalar dependencias

```bash
# Desde payment-service/
python -m venv venv
source venv/Scripts/activate

# Verificar que estás en el venv (deberías ver (venv) en tu prompt)
which python  # Debe apuntar a venv/Scripts/python

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 4 — Iniciar el servicio

```bash
# Asegúrate de estar en payment-service/ con venv activado
python -m src.main
```

> Cuando veas `✅ Payment Service started successfully`, el servicio está listo en http://localhost:3002

### Paso 5 — Probar endpoints

Abre **otra pestaña de Git Bash** (deja el servicio corriendo) y ejecuta:

```bash
# Health check — debe responder {"status":"healthy"}
curl http://localhost:3002/health

# Iniciar una saga de pago
SAGA_RESPONSE=$(curl -s -X POST http://localhost:3002/api/v1/sagas \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 100.00,
    "currency": "USD"
  }')

echo "$SAGA_RESPONSE"

# Extraer el saga_id de la respuesta
SAGA_ID=$(echo "$SAGA_RESPONSE" | grep -o '"saga_id":"[^"]*"' | cut -d'"' -f4)
echo "Saga ID: $SAGA_ID"
```

> Guarda el `saga_id` que aparece en la respuesta, lo necesitas para los siguientes comandos.
> Reemplaza `{sagaId}` con ese ID en los comandos de abajo.

```bash
# Obtener estado de la saga
curl http://localhost:3002/api/v1/sagas/{sagaId}

# Listar todas las sagas
curl http://localhost:3002/api/v1/sagas

# Forzar compensación (rollback) de una saga
curl -X POST http://localhost:3002/api/v1/sagas/{sagaId}/compensate
```

### Paso 6 — Verificar datos en DynamoDB (opcional)

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Ver todas las sagas guardadas
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name payment-sagas
```

### Probar Happy Path (Saga exitosa)

El Mock Payment Gateway tiene un 80% de tasa de éxito. Si creas varias sagas, algunas completarán exitosamente:

```bash
# Crear múltiples sagas para ver diferentes resultados
for i in {1..5}; do
  curl -s -X POST http://localhost:3002/api/v1/sagas \
    -H "Content-Type: application/json" \
    -d "{\"booking_id\":\"550e8400-e29b-41d4-a716-44665544000$i\",\"amount\":100.00,\"currency\":\"USD\"}" \
    | grep -o '"status":"[^"]*"'
  echo ""
done
```

### Probar Failure Path (Compensación)

Algunas sagas fallarán automáticamente (20% de probabilidad) y ejecutarán compensación. Puedes forzar compensación manualmente:

```bash
# Forzar compensación de una saga específica
curl -X POST http://localhost:3002/api/v1/sagas/{sagaId}/compensate
```

### Desactivar Virtual Environment

```bash
# Cuando termines de trabajar
deactivate
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

## ✅ Estado Actual

- [x] Domain Layer (100%)
- [x] Application Layer (100%)
- [x] Infrastructure Layer (100%)
- [x] REST API (100%)
- [x] Tests unitarios (70+ tests passing)
- [x] DynamoDB configurado con GSI
- [x] Script de inicialización
- [ ] Tests de integración con LocalStack
- [ ] SQS Consumer para BookingCreated events
- [ ] Integración end-to-end con Booking Service

## 🛠️ Troubleshooting

**Error: "Connection refused" al iniciar el servicio**
- Verifica que LocalStack está corriendo: `docker ps`
- Verifica que creaste la tabla DynamoDB (Paso 2)

**Error: "Table does not exist"**
- Ejecuta de nuevo el script: `bash scripts/init-dynamodb.sh`

**Error: "Port 3002 already in use"**
- Desde Git Bash: encuentra y detén el proceso
  ```bash
  # Ver qué proceso usa el puerto 3002
  netstat -ano | grep :3002
  # Copia el PID y ejecuta desde PowerShell:
  # Stop-Process -Id <PID> -Force
  ```

**Error: "ModuleNotFoundError: No module named 'fastapi'"**
- Asegúrate de tener el virtual environment activado (deberías ver `(venv)` en tu prompt)
- Si no está activado: `source venv/Scripts/activate`
- Reinstala dependencias: `pip install -r requirements.txt`

**Error: "No module named 'src'"**
- Asegúrate de estar en el directorio `payment-service/`
- Ejecuta: `python -m src.main` (no `python src/main.py`)

## 📚 Conceptos Clave

**Saga Pattern:** Transacciones distribuidas sin 2PC (Two-Phase Commit)
**Orchestration:** Coordinador central que controla el flujo
**Compensation:** Rollback semántico para deshacer operaciones
**Idempotencia:** Operaciones que pueden ejecutarse múltiples veces sin efectos secundarios
**State Machine:** Control de estados y transiciones válidas

## 📝 Notas de Diseño

### ¿Por qué Virtual Environment?

**Problema sin venv:**
- Dependencias se instalan globalmente
- Conflictos entre proyectos (Proyecto A usa FastAPI 0.100, Proyecto B usa 0.109)
- Difícil reproducir entorno en otro equipo

**Solución con venv:**
- ✅ Aislamiento completo de dependencias
- ✅ Cada proyecto tiene sus propias versiones
- ✅ Fácil de reproducir (requirements.txt)
- ✅ No contamina Python global

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

### Buenas Prácticas Implementadas

**Gestión de Dependencias:**
- ✅ Virtual environment (venv)
- ✅ requirements.txt con versiones específicas
- ✅ .gitignore para no commitear venv/

**Configuración:**
- ✅ .env para variables de entorno
- ✅ .env.example como documentación
- ✅ python-dotenv para cargar variables

**Testing:**
- ✅ pytest con configuración profesional
- ✅ Cobertura mínima del 70%
- ✅ Tests separados (unit, integration)
- ✅ Markers para categorizar tests

**Código Limpio:**
- ✅ Black para formateo automático
- ✅ Flake8 para linting
- ✅ MyPy para type checking
- ✅ Isort para ordenar imports

**Arquitectura:**
- ✅ Hexagonal Architecture (Ports & Adapters)
- ✅ Separación clara de capas
- ✅ Domain-Driven Design
- ✅ SOLID principles

### Manejo de Errores

- **Reintentos:** Exponential backoff para fallos transitorios
- **DLQ:** Dead Letter Queue para fallos permanentes
- **Alertas:** CloudWatch alarms para sagas atascadas
- **Timeout:** Sagas que no completan en X tiempo
