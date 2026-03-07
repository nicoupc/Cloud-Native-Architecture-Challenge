# Notification Service - Buffer Pattern

Microservicio de notificaciones con patrón Buffer para procesamiento asíncrono de mensajes.

## 🎯 Patrón Arquitectónico: Buffer Pattern

El Buffer Pattern es un patrón para desacoplar productores y consumidores de mensajes usando una cola (buffer). Permite procesar mensajes de forma asíncrona, con reintentos automáticos y manejo de fallos.

### ¿Por qué Buffer Pattern?

**Problema:**
Enviar notificaciones de forma síncrona puede:
- Bloquear el flujo principal si el servicio de email falla
- Perder mensajes si el servicio está caído
- No escalar bien con alto volumen de notificaciones

**Solución:**
Buffer Pattern usa SQS como cola intermedia:
- Productores publican mensajes a SQS
- Consumidores procesan mensajes de forma asíncrona
- Reintentos automáticos si falla el procesamiento
- Dead Letter Queue (DLQ) para mensajes que fallan repetidamente

### Buffer Pattern vs Direct Call

**Direct Call (sin buffer):**
- ❌ Acoplamiento fuerte
- ❌ Sin reintentos automáticos
- ❌ Pierde mensajes si el servicio falla
- ❌ No escala bien

**Buffer Pattern (con SQS):**
- ✅ Desacoplamiento total
- ✅ Reintentos automáticos
- ✅ Persistencia de mensajes
- ✅ Escalabilidad horizontal
- ✅ DLQ para mensajes fallidos

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                 Notification Service                        │
│                   (Buffer Pattern)                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Domain Layer                            │  │
│  │  ┌────────────────┐  ┌──────────────────────────┐   │  │
│  │  │  Notification  │  │   Email Templates        │   │  │
│  │  │   (Aggregate)  │  │   - BookingConfirmed     │   │  │
│  │  │                │  │   - PaymentProcessed     │   │  │
│  │  └────────────────┘  └──────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Application Layer                          │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │      Notification Processor                    │  │  │
│  │  │  - processMessage()                            │  │  │
│  │  │  - sendEmail()                                 │  │  │
│  │  │  - handleFailure()                             │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Infrastructure Layer                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐   │  │
│  │  │   SQS    │  │   DLQ    │  │  Mock Email     │   │  │
│  │  │ Consumer │  │  (Failed)│  │    Provider     │   │  │
│  │  └──────────┘  └──────────┘  └─────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Message Flow

### Happy Path (Éxito)

```
1. EventBridge → SQS Queue
   ↓
2. Consumer polls SQS (long polling)
   ↓
3. Process message (send email)
   ↓
4. Delete message from queue
   ↓
5. COMPLETED
```

### Failure Path (Reintentos y DLQ)

```
1. EventBridge → SQS Queue
   ↓
2. Consumer polls SQS
   ↓
3. Process message → FALLO
   ↓
4. Message vuelve a la cola (visibility timeout)
   ↓
5. Reintento 1, 2, 3... (hasta maxReceiveCount)
   ↓
6. Si sigue fallando → DLQ
   ↓
7. Alerta para revisión manual
```

## 📊 SQS Configuration

### Main Queue: notification-queue
- **Visibility Timeout:** 30 segundos
- **Message Retention:** 4 días
- **Max Receive Count:** 3 (después va a DLQ)
- **Long Polling:** 20 segundos

### Dead Letter Queue: notification-dlq
- **Message Retention:** 14 días
- **Purpose:** Almacenar mensajes que fallaron 3+ veces
- **Action:** Revisión manual y corrección

## 🔑 Conceptos Clave

### 1. Long Polling

Reduce costos y latencia al esperar mensajes:

```python
# Short polling (❌ ineficiente)
messages = sqs.receive_message(WaitTimeSeconds=0)  # Retorna inmediatamente

# Long polling (✅ eficiente)
messages = sqs.receive_message(WaitTimeSeconds=20)  # Espera hasta 20s
```

### 2. Visibility Timeout

Evita que múltiples consumidores procesen el mismo mensaje:

```python
# Mensaje se vuelve invisible por 30 segundos
messages = sqs.receive_message(VisibilityTimeout=30)

# Si no se elimina en 30s, vuelve a estar disponible
# Esto permite reintentos automáticos
```

### 3. Batch Processing

Procesa múltiples mensajes a la vez para eficiencia:

```python
# Recibir hasta 10 mensajes
messages = sqs.receive_message(MaxNumberOfMessages=10)

# Procesar en batch
for message in messages:
    process(message)
    
# Eliminar en batch
sqs.delete_message_batch(messages)
```

## 📦 Componentes

### Domain Layer
- **Notification:** Aggregate root
- **NotificationType:** Enum (BOOKING_CONFIRMED, PAYMENT_PROCESSED, etc.)
- **EmailTemplate:** Value object con plantillas HTML
- **Domain Events:** NotificationSent, NotificationFailed

### Application Layer
- **NotificationProcessor:** Procesa mensajes de SQS
- **EmailService:** Envía emails (mock)
- **MessageHandler:** Maneja diferentes tipos de notificaciones

### Infrastructure Layer
- **SQSConsumer:** Polling de mensajes
- **MockEmailProvider:** Simula envío de emails
- **EventBridgeSubscriber:** Suscripción a eventos

## 🚀 Inicio Rápido

### Prerequisitos
- Python 3.11+ instalado
- LocalStack corriendo (`docker-compose up -d`)
- SQS queues configuradas

### Instalación Profesional

```bash
# 1. Navegar al directorio del servicio
cd notification-service

# 2. Crear virtual environment
python -m venv venv

# 3. Activar virtual environment (Git Bash en Windows)
source venv/Scripts/activate

# 4. Actualizar pip
pip install --upgrade pip

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Copiar configuración
cp .env.example .env
```

### Desarrollo

```bash
# Iniciar consumer (procesa mensajes de SQS)
python -m src.main
```

### Tests

```bash
pytest
pytest --cov=src  # Con cobertura
```

## 🧪 Testing (Git Bash)

> ⚠️ Todos los comandos son para **Git Bash** en Windows.

### Paso 1 — Iniciar LocalStack

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar SQS
curl -s http://localhost:4566/_localstack/health | grep sqs
```

### Paso 2 — Crear SQS Queues

```bash
# Desde la raíz del proyecto
cd notification-service
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

bash scripts/init-sqs.sh
```

### Paso 3 — Activar venv e iniciar servicio

```bash
source venv/Scripts/activate
python -m src.main
```

### Paso 4 — Enviar mensaje de prueba

```bash
# En otra terminal
aws --endpoint-url=http://localhost:4566 sqs send-message \
  --queue-url http://localhost:4566/000000000000/notification-queue \
  --message-body '{"type":"BOOKING_CONFIRMED","bookingId":"123","email":"user@example.com"}'
```

## ✅ Estado Actual

- [ ] Domain Layer
- [ ] Application Layer
- [ ] Infrastructure Layer
- [ ] SQS Consumer
- [ ] Mock Email Provider
- [ ] Tests unitarios
- [ ] Script de inicialización

## 🛠️ Troubleshooting

**Error: "Queue does not exist"**
- Ejecuta: `bash scripts/init-sqs.sh`

**Error: "No messages received"**
- Verifica que EventBridge está publicando eventos
- Verifica la regla de EventBridge → SQS

**Mensajes en DLQ:**
- Revisa logs para ver el error
- Corrige el problema
- Reenvía mensajes desde DLQ a la cola principal

## 📚 Conceptos Clave

**Buffer Pattern:** Desacoplamiento con cola intermedia
**Long Polling:** Espera eficiente de mensajes
**Visibility Timeout:** Previene procesamiento duplicado
**DLQ:** Manejo de mensajes fallidos
**Batch Processing:** Procesamiento eficiente en lotes
