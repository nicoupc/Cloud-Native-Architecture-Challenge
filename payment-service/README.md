# Payment Service - Saga Pattern

Microservicio de procesamiento de pagos con patrón Saga para coordinar transacciones distribuidas.

> ⚠️ Todos los comandos son para **Git Bash** en Windows.
> Abre Git Bash y ubícate en la raíz del proyecto antes de empezar.

---

## ¿Qué hace este servicio?

Cuando alguien hace una reserva, este servicio se encarga de **cobrar el pago** coordinando varios pasos en orden:

```
1. Reservar el booking   → avisa al Booking Service
2. Procesar el pago      → cobra al cliente (simulado)
3. Confirmar el booking  → avisa al Booking Service que el pago fue exitoso
4. Enviar notificación   → avisa al cliente via EventBridge
```

Si **algún paso falla**, el servicio deshace automáticamente todo lo anterior (compensación).

---

## 🚀 Inicio Rápido (paso a paso)

### Prerequisitos
- Python 3.11+
- LocalStack corriendo (`docker-compose up -d` en la raíz del proyecto)
- Booking Service corriendo en puerto 3001

---

### Paso 1 — Iniciar LocalStack

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que está healthy
curl -s http://localhost:4566/_localstack/health | grep dynamodb
# Debe mostrar: "dynamodb": "available"  (o "running")
```

---

### Paso 2 — Crear tabla DynamoDB para los pagos

> ⚠️ **Solo necesitas hacer esto UNA VEZ.** Los datos persisten en `localstack-data/`.

```bash
# Desde la raíz del proyecto
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

bash init-payment-dynamodb.sh
```

> Si ves `La tabla 'payment-sagas' ya existe` — está bien ✅, ya fue creada antes.

---

### Paso 3 — Instalar dependencias

```bash
cd payment-service

# Crear entorno virtual (solo la primera vez)
python -m venv venv

# Activar entorno virtual
source venv/Scripts/activate
# Verás (venv) al inicio de tu prompt

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
cp .env.example .env
```

---

### Paso 4 — Iniciar el servicio

```bash
# Asegúrate de tener (venv) activo en tu prompt
uvicorn src.main:app --reload --port 3002 --host 0.0.0.0
```

Cuando veas:
```
INFO:     Uvicorn running on http://0.0.0.0:3002
```
El servicio está listo ✅

---

### Paso 5 — Probar el servicio

Abre **otra pestaña de Git Bash** (deja el servicio corriendo) y ejecuta:

```bash
# Health check — debe responder {"status":"healthy"}
curl http://localhost:3002/health

# Iniciar una saga de pago
curl -s -X POST http://localhost:3002/api/v1/sagas \
  -H "Content-Type: application/json" \
  -d '{"booking_id":"550e8400-e29b-41d4-a716-446655440000","amount":100.00,"currency":"USD"}'
```

> Guarda el `saga_id` que aparece en la respuesta. El estado inicial es `STARTED`.

> 💡 **Normal en esta fase:** El saga intentará conectar al Booking Service (puerto 3001).  
> Como aún no está corriendo junto a este servicio de forma integrada, verás `"status": "COMPENSATED"` — eso **es el comportamiento correcto** del patrón Saga: si un paso falla, deshace todo automáticamente.

```bash
# Consultar estado de la saga (reemplaza {sagaId} con el ID real)
curl http://localhost:3002/api/v1/sagas/{sagaId}

# Ver todas las sagas
curl http://localhost:3002/api/v1/sagas

# Forzar compensación (rollback) de una saga
curl -X POST http://localhost:3002/api/v1/sagas/{sagaId}/compensate
```

---

### Paso 6 — Correr los tests

```bash
# Con (venv) activado, desde la carpeta payment-service
pytest tests/unit/ --no-cov -q
# Resultado esperado: 74 passed
```

---

## 🛠️ Troubleshooting

**Error: `ModuleNotFoundError`**
- El entorno virtual no está activado: `source venv/Scripts/activate`

**Error: `Connection refused` en puerto 4566**
- LocalStack no está corriendo: `docker-compose up -d`

**Error: `Connection refused` en puerto 3001**
- El Booking Service no está corriendo: `cd booking-service && npm run dev`

**Desactivar el entorno virtual cuando termines:**
```bash
deactivate
```

---

## 🏗️ Arquitectura (resumen)

```
Cliente
  │
  └── POST /api/v1/sagas ──→ Payment Service
                                  │
                          1. Reserve Booking  ──→ Booking Service (puerto 3001)
                          2. Process Payment  ──→ Mock Gateway (simulado)
                          3. Confirm Booking  ──→ Booking Service (puerto 3001)
                          4. Send Notification ──→ EventBridge (LocalStack)
                                  │
                              COMPLETED ✅
                         (o COMPENSATED si falla ❌)
```

**Tecnologías:**
- **FastAPI** — framework web de Python (como Express en Node.js)
- **DynamoDB** — guarda el estado de cada pago
- **EventBridge** — publica eventos cuando el pago termina
- **venv** — entorno virtual para aislar las dependencias de Python

---

## ✅ Estado Actual

- ✅ Domain Layer — Saga, State Machine, Value Objects
- ✅ Application Layer — Saga Orchestrator
- ✅ Infrastructure Layer — DynamoDB, EventBridge, Mock Payment Gateway
- ✅ REST API — 4 endpoints
- ✅ Tests unitarios (74 tests)
