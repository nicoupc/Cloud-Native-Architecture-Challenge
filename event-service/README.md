# Event Service - Hexagonal Architecture

Microservicio de gestión de eventos implementando Hexagonal Architecture (Ports & Adapters).

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE LAYER                     │
│  ┌──────────────┐              ┌──────────────────────────┐ │
│  │ REST API     │              │ PostgreSQL Adapter       │ │
│  │ (IN Adapter) │              │ (OUT Adapter)            │ │
│  └──────┬───────┘              └──────────┬───────────────┘ │
│         │                                  │                 │
│         │                                  │                 │
│  ┌──────▼──────────────────────────────────▼───────────────┐│
│  │              APPLICATION LAYER                           ││
│  │  ┌────────────────────────────────────────────────────┐ ││
│  │  │ CreateEventService (Use Case)                      │ ││
│  │  └────────────────────────────────────────────────────┘ ││
│  └──────────────────────────────────────────────────────────┘│
│         │                                  │                 │
│         │                                  │                 │
│  ┌──────▼──────────────────────────────────▼───────────────┐│
│  │              DOMAIN LAYER (Core Business Logic)         ││
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────┐  ││
│  │  │ Event      │  │ Value Objects│  │ EventRepository│  ││
│  │  │ (Aggregate)│  │ (Immutable)  │  │ (Port)         │  ││
│  │  └────────────┘  └──────────────┘  └────────────────┘  ││
│  └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### 1. Iniciar LocalStack

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Inicializar PostgreSQL
bash init-localstack.sh
```

### 2. Ejecutar el servicio

```bash
cd event-service
mvn spring-boot:run
```

### 3. Probar el API

```bash
# Health check
curl http://localhost:8080/api/v1/events/health

# Crear evento
curl -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Concierto Radiohead 2026",
    "description": "Concierto en vivo",
    "type": "CONCERT",
    "eventDate": "2026-12-31T20:00:00",
    "capacity": 50000,
    "price": "150.00"
  }'
```

## 📦 Componentes

### Domain Layer (Núcleo de Negocio)

- **Event** (Aggregate): Entidad principal con lógica de negocio
- **Value Objects**: EventId, Capacity, Price, EventType, EventStatus
- **Ports**: EventRepository (interface)

### Application Layer (Casos de Uso)

- **CreateEventService**: Orquesta la creación de eventos

### Infrastructure Layer (Adaptadores)

- **REST API**: EventController (IN Adapter)
- **PostgreSQL**: PostgresEventRepositoryAdapter (OUT Adapter)
- **JPA**: EventEntity, JpaEventRepository, EventMapper

## 🧪 Testing

```bash
# Tests unitarios
mvn test

# Tests con cobertura
mvn test jacoco:report
```

## 🗄️ Base de Datos

### Conexión PostgreSQL (LocalStack)

```yaml
Host: localhost
Port: 4510
Database: events_db
Username: test
Password: test
```

### Migraciones Flyway

Las migraciones se ejecutan automáticamente al iniciar:

- `V1__create_events_table.sql`: Crea tabla events con índices

## 📚 Patrones Implementados

### Hexagonal Architecture

- **Ports**: Interfaces que definen contratos (EventRepository)
- **Adapters**: Implementaciones concretas (PostgresEventRepositoryAdapter)
- **Domain Independence**: El dominio NO conoce Spring Boot, JPA, ni PostgreSQL

### Domain-Driven Design

- **Aggregates**: Event (raíz del agregado)
- **Value Objects**: Objetos inmutables (EventId, Capacity, Price)
- **Factory Methods**: Event.create() garantiza validez

### Dependency Inversion

- El dominio define QUÉ necesita (Port)
- La infraestructura define CÓMO lo hace (Adapter)
- Spring Boot conecta todo automáticamente

## 🔧 Configuración

### application.yml

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:4510/events_db
  jpa:
    hibernate:
      ddl-auto: validate  # Flyway maneja migraciones
  flyway:
    enabled: true
```

## 📝 Convenciones de Código

- **Domain**: Sin dependencias externas (Java puro)
- **Application**: Solo depende del Domain
- **Infrastructure**: Depende de Domain y frameworks

## 🎯 Próximos Pasos

- [ ] Agregar EventBridge para publicar eventos
- [ ] Implementar más endpoints (GET, PUT, DELETE)
- [ ] Agregar validaciones con Bean Validation
- [ ] Implementar Exception Handling global
- [ ] Agregar logging estructurado
