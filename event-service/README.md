# Event Service - Hexagonal Architecture

Microservicio de gestión de eventos con PostgreSQL RDS en LocalStack.

> ⚠️ Todos los comandos son para **Git Bash** en Windows.
> Abre Git Bash y ubícate en la raíz del proyecto antes de empezar.

## 🚀 Inicio Rápido

### Prerequisitos

- Docker y Docker Compose
- Java 17+ (Amazon Corretto recomendado)
- Maven (`choco install maven -y` desde PowerShell como administrador)
- Git Bash

---

### Paso 1 — Iniciar LocalStack

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Verificar que está healthy (~10 segundos)
curl -s http://localhost:4566/_localstack/health | grep rds
# Debe mostrar: "rds": "available"
```

---

### Paso 2 — Crear Base de Datos PostgreSQL y EventBridge

> ⚠️ **Solo necesitas hacer esto UNA VEZ.** Los datos persisten en `localstack-data/`.
> Solo repite este paso si borras esa carpeta o ejecutas `docker-compose down -v`.

```bash
# Desde la raíz del proyecto
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

bash init-localstack.sh
bash init-eventbridge.sh
```

> ⏳ **Después de ejecutar los scripts, espera ~30 segundos** antes de pasar al Paso 3.
> El RDS necesita tiempo para inicializarse. Puedes verificar que está listo con:
> ```bash
> aws --endpoint-url=http://localhost:4566 rds describe-db-instances --query "DBInstances[0].DBInstanceStatus"
> # Debe mostrar: "available"  (si muestra "creating", espera unos segundos más)
> ```

---

### Paso 3 — Ejecutar el Event Service

```bash
cd event-service
mvn spring-boot:run
```

Espera a ver en los logs:
```
Started EventServiceApplication in X.XXX seconds
```

---

### Paso 4 — Probar el API

Abre **otra pestaña de Git Bash** (deja el servicio corriendo) y ejecuta:

```bash
# Health check — debe responder: Event Service is running!
curl http://localhost:8080/api/v1/events/health
```

```bash
# Crear un evento (desde la raíz del proyecto)
EVENT_ID=$(curl -s -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d @test-create-event.json | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "Evento creado con ID: $EVENT_ID"
```

```bash
# Publicar el evento
curl -s -X POST http://localhost:8080/api/v1/events/$EVENT_ID/publish
```

Verás en los logs del servicio que el evento fue publicado a EventBridge.

---

## 🧪 Tests

```bash
cd event-service
mvn test
```

Resultado esperado: `Tests run: 10, Failures: 0, Errors: 0`

---

## 🗄️ Ver los Datos en PostgreSQL (opcional)

```bash
# Conectar a la base de datos (requiere psql instalado)
psql -h localhost -p 4510 -U postgres -d events_db

# Ver eventos
SELECT * FROM events;

# Salir
\q
```

También puedes usar **DBeaver** (GUI):
- Host: `localhost`, Port: `4510`, Database: `events_db`
- Username: `postgres`, Password: `postgres`

---

## 🛠️ Troubleshooting

**Error: "Connection refused" al iniciar el servicio**
- Verifica que LocalStack está corriendo: `docker ps`
- Verifica que creaste la base de datos (Paso 2)

**Error: "Database does not exist"**
- Ejecuta de nuevo el Paso 2

**Error: "Port 8080 already in use"**
- Desde Git Bash: encuentra y detén el proceso
  ```bash
  # Ver qué proceso usa el puerto 8080
  netstat -ano | grep :8080
  # Copia el PID y ejecuta desde PowerShell:
  # Stop-Process -Id <PID> -Force
  ```

---

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

---

## 🎯 Estado Actual

- ✅ Hexagonal Architecture (Ports & Adapters)
- ✅ Domain-Driven Design (Aggregates, Value Objects, Domain Events)
- ✅ Event-Driven Architecture (EventBridge)
- ✅ PostgreSQL RDS en LocalStack
- ✅ Flyway Migrations
- ✅ Tests unitarios (10 tests)
- ✅ Transacciones distribuidas con @Transactional

**Preparado para migrar a AWS:** Solo cambiar el datasource URL a RDS real y remover el endpoint-url de EventBridge.

