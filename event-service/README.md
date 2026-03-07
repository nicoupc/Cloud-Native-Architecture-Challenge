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

### Paso 2: Crear Base de Datos PostgreSQL

**Solo necesitas hacer esto UNA VEZ.** Los datos persisten automáticamente en la carpeta `localstack-data/`.
Solo necesitarás repetirlo si borras esa carpeta o usas `docker-compose down -v` (que elimina los volúmenes).

**En Windows (PowerShell):**
```powershell
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
```

**En Mac/Linux (Git Bash):**
```bash
# Desde la raíz del proyecto
bash init-localstack.sh
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
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/events" -Method POST -Body $body -ContentType "application/json"
```

**Crear un Evento (Git Bash / Mac / Linux):**
```bash
# Desde la raíz del proyecto
curl -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d @test-create-event.json
```

Verás el evento creado con su ID.

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

- **Domain Layer:** Event (Aggregate), EventId, Capacity, Price, EventType, EventStatus
- **Application Layer:** CreateEventService (Use Case)
- **Infrastructure Layer:** 
  - EventController (REST API)
  - PostgresEventRepositoryAdapter (PostgreSQL)
  - EventEntity, EventMapper (JPA)

## 🔄 Flujo de Datos

1. Cliente → REST API (EventController)
2. Controller → Application Service (CreateEventService)
3. Service → Domain (Event.create())
4. Service → Repository Port (EventRepository interface)
5. Port → Adapter (PostgresEventRepositoryAdapter)
6. Adapter → PostgreSQL RDS (LocalStack)

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

- [ ] EventBridge integration (publicar eventos)
- [ ] Más endpoints REST (GET, PUT, DELETE)
- [ ] Exception handling global
- [ ] Logging estructurado
- [ ] Migración a AWS real

Este proyecto demuestra:
- ✅ Hexagonal Architecture (Ports & Adapters)
- ✅ Domain-Driven Design (Aggregates, Value Objects)
- ✅ PostgreSQL RDS en LocalStack
- ✅ Flyway Migrations
- ✅ Spring Boot con JPA
- ✅ Tests unitarios completos

**Preparado para migrar a AWS:** Solo cambiar el datasource URL a RDS real.
