# Event Service - Hexagonal Architecture

Microservicio de gestión de eventos con PostgreSQL RDS en LocalStack.

## 🚀 Inicio Rápido

### Prerequisitos

- Docker y Docker Compose
- Java 17+
- Maven (instalado con `choco install maven -y`)

### Paso 1: Iniciar LocalStack

```powershell
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que está corriendo
curl http://localhost:4566/_localstack/health
```

### Paso 2: Crear Base de Datos PostgreSQL y EventBridge

**Solo necesitas hacer esto UNA VEZ.** Los datos persisten automáticamente en la carpeta `localstack-data/`.
Solo necesitarás repetirlo si borras esa carpeta o usas `docker-compose down -v` (que elimina los volúmenes).

**Opción A: Script automático (Recomendado)**

```bash
# Desde la raíz del proyecto (Git Bash / Mac / Linux)
bash init-localstack.sh
bash init-eventbridge.sh
```

**Opción B: Manual (Windows PowerShell)**

```powershell
# 1. Crear PostgreSQL RDS
$env:AWS_ACCESS_KEY_ID = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
$env:AWS_DEFAULT_REGION = "us-east-1"

aws --endpoint-url=http://localhost:4566 rds create-db-instance `
    --db-instance-identifier events-db `
    --db-instance-class db.t3.micro `
    --engine postgres `
    --engine-version 14.7 `
    --master-username postgres `
    --master-user-password postgres `
    --allocated-storage 20 `
    --db-name events_db `
    --port 4510 `
    --region us-east-1

# 2. Crear EventBridge Bus
aws --endpoint-url=http://localhost:4566 events create-event-bus `
    --name event-management-bus `
    --region us-east-1
```

### Paso 3: Ejecutar el Event Service

```powershell
cd event-service
mvn spring-boot:run
```

Espera a ver: `Started EventServiceApplication in X.XXX seconds`

### Paso 4: Probar el API

**Health Check:**
```powershell
curl http://localhost:8080/api/v1/events/health
```

Respuesta: `Event Service is running!`

**Crear un Evento (PowerShell):**
```powershell
$body = Get-Content ..\test-create-event.json -Raw
$response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/events" -Method POST -Body $body -ContentType "application/json"
$eventId = $response.id
Write-Host "Evento creado con ID: $eventId"
```

**Publicar el Evento (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/events/$eventId/publish" -Method POST
```

**Crear un Evento (Git Bash / Mac / Linux):**
```bash
# Desde la raíz del proyecto
EVENT_ID=$(curl -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d @test-create-event.json | jq -r '.id')

echo "Evento creado con ID: $EVENT_ID"
```

**Publicar el Evento (Git Bash / Mac / Linux):**
```bash
curl -X POST http://localhost:8080/api/v1/events/$EVENT_ID/publish
```

Verás el evento publicado y un mensaje en los logs indicando que se publicó a EventBridge.

## 🗄️ Ver los Datos en PostgreSQL

### Opción 1: Usando psql (línea de comandos)

```bash
# Conectar a la base de datos
psql -h localhost -p 4510 -U postgres -d events_db

# Ver todas las tablas
\dt

# Ver eventos
SELECT * FROM events;

# Salir
\q
```

### Opción 2: Usando DBeaver (GUI)

1. Descargar DBeaver: https://dbeaver.io/download/
2. Crear nueva conexión PostgreSQL:
   - Host: `localhost`
   - Port: `4510`
   - Database: `events_db`
   - Username: `postgres`
   - Password: `postgres`
3. Conectar y explorar la tabla `events`

## 🧪 Tests

```bash
cd event-service
mvn test
```

Resultado esperado: `Tests run: 10, Failures: 0, Errors: 0`

## 🏗️ Arquitectura Hexagonal

```
┌─────────────────────────────────────────┐
│         Infrastructure Layer            │
│  ┌──────────┐      ┌─────────────────┐ │
│  │ REST API │      │ PostgreSQL RDS  │ │
│  │  (IN)    │      │     (OUT)       │ │
│  └────┬─────┘      └────────┬────────┘ │
│       │                     │          │
│  ┌────▼─────────────────────▼────────┐ │
│  │      Application Layer            │ │
│  │   (CreateEventService)            │ │
│  └────┬──────────────────────────────┘ │
│       │                                │
│  ┌────▼──────────────────────────────┐ │
│  │       Domain Layer                │ │
│  │  (Event, Value Objects, Ports)    │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Principio clave:** El dominio NO conoce PostgreSQL, Spring Boot, ni JPA.

## 📦 Componentes

- **Domain Layer:** 
  - Aggregates: Event
  - Value Objects: EventId, Capacity, Price, EventType, EventStatus
  - Domain Events: EventCreated, EventPublished, EventCancelled
  - Ports: EventRepository, EventPublisher
  - Exceptions: EventNotFoundException, InvalidEventStateException, EventPublishingException

- **Application Layer:** 
  - Use Cases: CreateEventService, PublishEventService

- **Infrastructure Layer:** 
  - REST API: EventController
  - PostgreSQL Adapter: PostgresEventRepositoryAdapter, EventEntity, EventMapper
  - EventBridge Adapter: EventBridgePublisherAdapter
  - Configuration: ApplicationConfig, AwsConfig

## 🔄 Flujo de Datos

### Crear Evento:
1. Cliente → REST API (EventController)
2. Controller → Application Service (CreateEventService)
3. Service → Domain (Event.create())
4. Service → Repository Port (EventRepository interface)
5. Port → Adapter (PostgresEventRepositoryAdapter)
6. Adapter → PostgreSQL RDS (LocalStack)

### Publicar Evento:
1. Cliente → REST API (POST /events/{id}/publish)
2. Controller → Application Service (PublishEventService)
3. Service → Repository (cargar evento)
4. Service → Domain (Event.publish() - DRAFT → PUBLISHED)
5. Service → Repository (guardar evento actualizado)
6. Service → EventPublisher Port (publicar EventPublished)
7. Port → Adapter (EventBridgePublisherAdapter)
8. Adapter → EventBridge (LocalStack)
9. **@Transactional:** Si EventBridge falla, rollback automático

## 🛠️ Troubleshooting

**Error: "Connection refused" al iniciar el servicio**
- Verifica que LocalStack está corriendo: `docker ps`
- Verifica que creaste la base de datos (Paso 2)

**Error: "Database does not exist"**
- Ejecuta de nuevo el comando del Paso 2 para crear la instancia RDS

**Error: "Port 8080 already in use"**
- Encuentra y detén el proceso que usa ese puerto (PowerShell):
  ```powershell
  # Ver qué proceso usa el puerto 8080
  netstat -ano | findstr :8080
  # Copia el PID (último número) y ejecútalo aquí:
  Stop-Process -Id <PID> -Force
  ```
- O cambia el puerto en `application.yml` (`server.port: 8081`)

## 🎯 Próximos Pasos

- [x] Domain layer con Hexagonal Architecture
- [x] Application layer con use cases
- [x] PostgreSQL persistence con JPA
- [x] EventBridge integration (publicar eventos)
- [x] REST API básica (POST /events, POST /events/{id}/publish)
- [ ] Más endpoints REST (GET, PUT, DELETE)
- [ ] Exception handling global
- [ ] Logging estructurado
- [ ] Tests de integración con Testcontainers
- [ ] Migración a AWS real

Este proyecto demuestra:
- ✅ Hexagonal Architecture (Ports & Adapters)
- ✅ Domain-Driven Design (Aggregates, Value Objects, Domain Events)
- ✅ Event-Driven Architecture (EventBridge)
- ✅ PostgreSQL RDS en LocalStack
- ✅ Flyway Migrations
- ✅ Spring Boot con JPA
- ✅ Tests unitarios completos
- ✅ Transacciones distribuidas con @Transactional

**Preparado para migrar a AWS:** Solo cambiar el datasource URL a RDS real y remover el endpoint-url de EventBridge.
