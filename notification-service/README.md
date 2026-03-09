# Notification Service - Buffer Pattern

Microservicio de notificaciones que usa SQS como cola intermedia para procesar emails de forma asíncrona.

> ⚠️ Todos los comandos son para **Git Bash** en Windows.
> Abre Git Bash y ubícate en la raíz del proyecto antes de empezar.

---

## ¿Qué hace este servicio?

Recibe mensajes de una cola SQS y **envía notificaciones por email** (simuladas con logs). Es el último eslabón del sistema: cuando un pago se procesa o una reserva se confirma, este servicio notifica al usuario.

```
SQS Queue
   │
   ├── BOOKING_CREATED    → "Tu reserva fue creada"
   ├── BOOKING_CONFIRMED  → "Tu reserva fue confirmada"
   ├── BOOKING_CANCELLED  → "Tu reserva fue cancelada"
   ├── PAYMENT_PROCESSED  → "Tu pago fue procesado"
   ├── PAYMENT_FAILED     → "Tu pago falló"
   ├── EVENT_PUBLISHED    → "Nuevo evento disponible"
   └── EVENT_CANCELLED    → "El evento fue cancelado"
```

Si un mensaje **falla 3 veces**, pasa automáticamente a la **Dead Letter Queue (DLQ)** para revisión manual — así nunca se pierde un mensaje.

---

## 🚀 Inicio Rápido (paso a paso)

### Prerequisitos
- Python 3.11+
- LocalStack corriendo (`docker-compose up -d` en la raíz del proyecto)

---

### Paso 1 — Iniciar LocalStack

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que está healthy
curl -s http://localhost:4566/_localstack/health | grep sqs
# Debe mostrar: "sqs": "available"  (o "running")
```

---

### Paso 2 — Crear las colas SQS

> ⚠️ **Solo necesitas hacer esto UNA VEZ.** Los datos persisten en `localstack-data/`.

```bash
# Desde la raíz del proyecto
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

bash init-notification-sqs.sh
```

> Si ves `QueueAlreadyExists` — está bien ✅, ya fueron creadas antes.

---

### Paso 3 — Instalar dependencias

```bash
cd notification-service

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
python -m src.main
```

Cuando veas:
```
INFO - Starting Notification Service...
INFO - Polling for messages from: notification-queue
```
El servicio está listo ✅ y escuchando mensajes.

---

### Paso 5 — Enviar un mensaje de prueba

Abre **otra pestaña de Git Bash** (deja el servicio corriendo) y ejecuta:

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Enviar notificación de reserva confirmada
aws --endpoint-url=http://localhost:4566 sqs send-message \
  --queue-url http://localhost:4566/000000000000/notification-queue \
  --message-body '{"type":"BOOKING_CONFIRMED","email":"user@example.com","bookingId":"booking-123","eventName":"Rock Concert","ticketQuantity":2,"totalPrice":100.0}'
```

En los logs del servicio deberías ver:
```
INFO - [MOCK] Email sent to user@example.com
Subject: Booking Confirmed - Event Management
Body preview: Dear Customer, Your booking has been confirmed!...
INFO - Notification sent successfully
INFO - Message processed successfully
```

---

### Paso 6 — Correr los tests

```bash
# Con (venv) activado, desde la carpeta notification-service
pytest tests/unit/ --no-cov -q
# Resultado esperado: 73 passed (82.08% statement coverage)
```

---

## 🛠️ Troubleshooting

**Error: `Queue does not exist`**
- Las colas no fueron creadas: `bash init-notification-sqs.sh`

**Error: `ModuleNotFoundError`**
- El entorno virtual no está activado: `source venv/Scripts/activate`

**Error: `Connection refused` en puerto 4566**
- LocalStack no está corriendo: `docker-compose up -d`

**No aparecen mensajes procesados:**
- Verifica que enviaste el mensaje a la URL correcta: `http://localhost:4566/000000000000/notification-queue`

**Desactivar el entorno virtual cuando termines:**
```bash
deactivate
```

---

## 🏗️ Arquitectura (resumen)

```
Otros servicios
      │
      └── Publican a SQS ──→ notification-queue
                                    │
                          SQSConsumer (polling c/20s)
                                    │
                          NotificationProcessor
                                    │
                          MockEmailProvider (logs)
                                    │
                               ENVIADO ✅
                     (o DLQ si falla 3 veces ❌)
```

**Tecnologías:**
- **FastAPI / asyncio** — event loop para polling continuo
- **SQS** — cola que absorbe picos de notificaciones (Buffer)
- **DLQ** — Dead Letter Queue para mensajes que fallan repetidamente
- **venv** — entorno virtual para aislar las dependencias de Python

---

## ✅ Estado Actual

- ✅ Domain Layer — Notification aggregate, value objects, email templates
- ✅ Application Layer — NotificationProcessor, MessageHandler
- ✅ Infrastructure Layer — SQSConsumer, MockEmailProvider
- ✅ REST API — Health check en puerto 3003
- ✅ Tests unitarios (73 tests, 82.08% statement coverage)
