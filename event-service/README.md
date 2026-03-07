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

# Verificar que LocalStack está corriendo
curl http://localhost:4566/_localstack/health

# Inicializar PostgreSQL RDS
bash init-localstack.sh
```

### 2. Ejecutar el servicio

**Opción A: Con H2 (desarrollo rápido)**
```bash
cd event-service
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

**Opción B: Con PostgreSQL RDS en LocalStack (producción local)**
```bash
cd event-service
mvn spring-boot:run -Dspring-boot.run.profiles=localstack
```

### 3. Probar el API

```bash
# Health check
curl http://localhost:8080/api/v1/events/health

# Crear evento
curl -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d @test-create-event.json
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

### Perfiles de Configuración

El servicio soporta dos perfiles:

**Profile: `local` (por defecto)**
- Base de datos: H2 in-memory
- Uso: Desarrollo rápido y tests
- No requiere LocalStack

**Profile: `localstack`**
- Base de datos: PostgreSQL RDS en LocalStack
- Uso: Ambiente similar a producción
- Requiere LocalStack corriendo

### Conexión PostgreSQL RDS (LocalStack)

```yaml
Host: localhost
Port: 4510
Database: events_db
Username: postgres
Password: postgres
```

### Migraciones Flyway

Las migraciones se ejecutan automáticamente al iniciar:

- `V1__create_events_table.sql`: Crea tabla events con índices y constraints

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

### application.yml - Perfiles

**Configuración Base (común a todos los perfiles)**
```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate  # Flyway maneja migraciones
  flyway:
    enabled: true
```

**Profile: local**
```yaml
spring:
  datasource:
    url: jdbc:h2:mem:events_db;MODE=PostgreSQL
    driver-class-name: org.h2.Driver
```

**Profile: localstack**
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:4510/events_db
    username: postgres
    password: postgres
    driver-class-name: org.postgresql.Driver
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
