# 🚀 Guía de Inicio Rápido — Cloud-Native Architecture Challenge

Guía paso a paso para levantar los 4 microservicios y verificar que todo funciona correctamente.

---

## 📋 Prerrequisitos

Antes de empezar, asegúrate de tener instalado:

| Herramienta | Versión mínima | Verificar con |
|-------------|---------------|---------------|
| **Docker Desktop** | 20+ | `docker --version` |
| **Java JDK** | 17+ | `java -version` |
| **Maven** | 3.8+ | `mvn -version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Python** | 3.10+ | `python --version` |
| **Git Bash** | (incluido con Git) | `bash --version` |

> **Nota Windows:** Los scripts `.sh` se ejecutan con Git Bash (`bash script.sh`).

---

## 🏗️ Paso 1: Levantar LocalStack (Infraestructura AWS)

LocalStack simula todos los servicios de AWS (DynamoDB, SQS, EventBridge, RDS, CloudWatch) localmente con Docker.

### 1.1 Iniciar el contenedor

```bash
docker-compose up -d
```

Espera ~30 segundos y verifica que esté saludable:

```bash
docker ps
# Deberías ver: localstack/localstack-pro ... (healthy)
```

### 1.2 Inicializar los servicios AWS

Ejecuta los 8 scripts de inicialización **en este orden exacto**:

```bash
# Base de datos PostgreSQL para Event Service
bash init-localstack.sh

# EventBridge (bus de eventos)
bash init-eventbridge.sh

# DynamoDB para Booking Service
bash init-dynamodb.sh

# DynamoDB para Payment Service
bash init-payment-dynamodb.sh

# Cola SQS para Notification Service
bash init-notification-sqs.sh

# Cola SQS para Booking Service + tabla EventAvailability
bash init-booking-sqs.sh

# Reglas de enrutamiento EventBridge (conecta los servicios)
bash init-eventbridge-rules.sh

# Grupos de logs CloudWatch
bash init-cloudwatch.sh
```

> **⏱️ Tip:** `init-localstack.sh` puede tardar ~30-60 segundos porque crea la base de datos PostgreSQL. Los demás son rápidos (~2-3 segundos cada uno).

### 1.3 Verificar que todo se creó correctamente

```bash
# Verificar EventBridge
aws --endpoint-url=http://localhost:4566 events list-event-buses --region us-east-1

# Verificar DynamoDB
aws --endpoint-url=http://localhost:4566 dynamodb list-tables --region us-east-1

# Verificar SQS
aws --endpoint-url=http://localhost:4566 sqs list-queues --region us-east-1

# Verificar PostgreSQL
docker exec -it $(docker ps -q) psql -h localhost -p 4510 -U postgres -d events_db -c "SELECT 1;"
```

---

## 🖥️ Paso 2: Iniciar los 4 Microservicios

Necesitas **4 terminales separadas**, una para cada servicio.

### 2.1 Terminal 1 — Event Service (Java/Spring Boot, puerto 8080)

```bash
cd event-service
mvn spring-boot:run
```

Espera a ver:
```
Started EventServiceApplication in X seconds
```

Verifica: [http://localhost:8080/api/v1/events/health](http://localhost:8080/api/v1/events/health)

### 2.2 Terminal 2 — Booking Service (Node.js/Express, puerto 3001)

```bash
cd booking-service
npm install    # solo la primera vez
npm run dev
```

Espera a ver:
```
✅ Booking Service started successfully!
📡 Server listening on port 3001
🔄 SQS Consumer started, polling: ...
```

Verifica: [http://localhost:3001/health](http://localhost:3001/health)

### 2.3 Terminal 3 — Payment Service (Python/FastAPI, puerto 3002)

```bash
cd payment-service
pip install -r requirements.txt    # solo la primera vez
uvicorn src.main:app --host 0.0.0.0 --port 3002
```

> **⚠️ Si `pip install` da error de permisos**, usa: `pip install --user -r requirements.txt`

Espera a ver:
```
✅ Payment Service started successfully
Uvicorn running on http://0.0.0.0:3002
```

Verifica: [http://localhost:3002/health](http://localhost:3002/health)

### 2.4 Terminal 4 — Notification Service (Python/asyncio, sin puerto HTTP)

```bash
cd notification-service
pip install -r requirements.txt    # solo la primera vez
python -m src.main
```

> **⚠️ Si `pip install` da error de permisos**, usa: `pip install --user -r requirements.txt`

Espera a ver:
```
Starting Notification Service
Queue URL: http://localhost:4566/000000000000/notification-queue
Starting SQS consumer for queue: ...
```

> **Nota:** Este servicio no tiene endpoint HTTP; consume mensajes de SQS automáticamente.

---

## ✅ Paso 3: Verificar que todo funciona

### 3.1 Health Checks rápidos

Abre una **5ta terminal** y ejecuta:

```bash
# Event Service
curl http://localhost:8080/api/v1/events/health

# Booking Service
curl http://localhost:3001/health

# Payment Service
curl http://localhost:3002/health
```

Los tres deben responder exitosamente.

### 3.2 Cargar datos de prueba (Seed Data)

```bash
bash seed-data.sh
```

Deberías ver:
```
✓ Created event: Summer Rock Festival
✓ Created event: Tech Innovation Conference
✓ Created event: Champions League Final Viewing
✓ Published event: Summer Rock Festival
✓ Published event: Tech Innovation Conference
✓ Created booking: 2 tickets for Summer Rock Festival
✓ Created booking: 1 ticket for Tech Innovation Conference
✓ Created booking: 5 tickets for Summer Rock Festival
✓ Created payment saga for Booking 1 ($150.00)
✓ Created payment saga for Booking 2 ($199.99)

Succeeded: 13 / 13
```

> **Importante:** Si ves `Succeeded: 13 / 13`, todo está perfecto. Si alguno falla, verifica que los 4 servicios estén corriendo.

### 3.3 Ejecutar Test E2E completo

```bash
bash test-e2e.sh
```

Este script prueba el flujo completo automáticamente:
1. Crear un evento → Publicarlo
2. Crear una reserva (booking)
3. Iniciar saga de pago
4. Verificar que la saga completó
5. Verificar que el booking se confirmó
6. Consultas CQRS (listar eventos, bookings por usuario)
7. Cancelar evento

Resultado esperado:
```
==========================================
 RESULTADOS E2E
==========================================
  Passed: 10
  Failed: 0
  Total:  10
==========================================
  ALL TESTS PASSED!
```

---

## 🧪 Paso 4: Probar manualmente con curl

Si quieres probar los endpoints uno por uno:

### Crear un evento

```bash
curl -s -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Evento de Prueba",
    "description": "Un evento increíble",
    "type": "CONCERT",
    "eventDate": "2027-06-15T20:00:00",
    "capacity": 1000,
    "price": "50.00",
    "locationVenue": "Estadio Nacional",
    "locationCity": "Lima",
    "locationCountry": "Peru"
  }'
```

> **Campos obligatorios:** `name`, `description`, `type` (CONCERT/CONFERENCE/SPORTS), `eventDate` (debe ser fecha futura), `capacity` (>0), `price`

### Publicar un evento

```bash
curl -s -X POST http://localhost:8080/api/v1/events/{EVENT_ID}/publish
```

### Crear una reserva (booking)

```bash
curl -s -X POST http://localhost:3001/api/v1/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "eventId": "{EVENT_ID}",
    "ticketQuantity": 2,
    "pricePerTicket": 50.00
  }'
```

> **Campos obligatorios:** `userId` (UUID válido), `eventId` (UUID válido), `ticketQuantity` (1-10), `pricePerTicket` (>0)

### Iniciar saga de pago

```bash
curl -s -X POST http://localhost:3002/api/v1/sagas \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "{BOOKING_ID}",
    "amount": 100.00,
    "currency": "USD"
  }'
```

### Ver estado de una saga

```bash
curl -s http://localhost:3002/api/v1/sagas/{SAGA_ID}
```

### Listar todos los eventos

```bash
curl -s http://localhost:8080/api/v1/events
```

### Ver bookings de un usuario

```bash
curl -s http://localhost:3001/api/v1/bookings/user/{USER_ID}
```

---

## 📮 Paso 5: Usar con Postman (Opcional)

El proyecto incluye una colección de Postman lista para usar:

1. Abre Postman
2. Importa el archivo `postman-collection.json` (está en la raíz del proyecto)
3. La colección tiene 4 carpetas:
   - **Event Service** (6 requests)
   - **Booking Service** (7 requests)
   - **Payment Service** (5 requests)
   - **Notification Service** (1 request)

---

## 🛑 Paso 6: Apagar todo

Cuando termines:

```bash
# Detener los 4 servicios: Ctrl+C en cada terminal

# Detener LocalStack
docker-compose down
```

Si quieres empezar desde cero (limpiar datos):

```bash
docker-compose down -v
rm -rf localstack-data/*
```

---

## 🔧 Troubleshooting — Errores Comunes

### ❌ "Puerto 8080 ya está en uso"
```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :8080
# Matarlo (reemplaza PID con el número)
taskkill /PID {PID} /F
```

### ❌ "pip install" da error de permisos
```bash
pip install --user -r requirements.txt
```

### ❌ "seed-data.sh falla" o "La fecha del evento debe ser futura"
Las fechas del seed data se calculan automáticamente. Si por alguna razón falla, verifica que `date` funcione en tu bash:
```bash
bash -c 'date -d "+1 year" +%Y'
```

### ❌ "PARSE_ERROR" en test-e2e.sh
El script necesita `python` (no `python3`) disponible en el PATH para parsear JSON. Verifica:
```bash
bash -c 'python --version'
```
Si no tienes Python en bash, instala `jq`:
```bash
# Con chocolatey (Windows)
choco install jq
# O descarga desde https://jqlang.github.io/jq/download/
```

### ❌ LocalStack no levanta / "(unhealthy)"
```bash
# Ver logs del contenedor
docker-compose logs localstack

# Verificar que el token es válido
cat .env | grep LOCALSTACK_AUTH_TOKEN
```

### ❌ Event Service no conecta a la base de datos
Asegúrate de que `init-localstack.sh` terminó correctamente antes de iniciar el Event Service. PostgreSQL tarda ~30-60 segundos en estar listo.

### ❌ "Cannot GET /api/v1/bookings/"
Probablemente el ID del booking está vacío. Asegúrate de reemplazar `{BOOKING_ID}` con un UUID real.

### ❌ Notification Service no procesa mensajes
Verifica que `init-eventbridge-rules.sh` se ejecutó correctamente. Este script crea las 7 reglas que enrutan eventos entre servicios.

---

## 📊 Resumen de la Arquitectura

```
┌─────────────────┐     EventBridge      ┌─────────────────┐
│  Event Service   │────(event-bus)──────▶│Booking Service   │
│  (Java:8080)     │                      │  (Node:3001)     │
│  PostgreSQL RDS  │                      │  DynamoDB        │
│  Hexagonal Arch  │                      │  CQRS Pattern    │
└─────────────────┘                      └─────────────────┘
        │                                        │
        │         EventBridge Rules               │
        ▼                                        ▼
┌─────────────────┐                      ┌─────────────────┐
│Payment Service   │◀──── Saga ─────────▶│Notification Svc  │
│  (Python:3002)   │                      │  (Python:SQS)    │
│  DynamoDB        │                      │  SQS Consumer    │
│  Saga Pattern    │                      │  Buffer Pattern  │
└─────────────────┘                      └─────────────────┘
```

**Flujo de eventos:**
1. Event Service publica eventos → EventBridge
2. EventBridge enruta a Booking (SQS) y Notification (SQS)
3. Booking Service crea reservas → EventBridge
4. Payment Service ejecuta sagas (4 pasos) → EventBridge
5. Notification Service consume y envía emails (mock)
