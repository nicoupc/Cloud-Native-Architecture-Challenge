# Diagrama C4 — Plataforma de Gestión de Eventos Cloud-Native

## Nivel 2: Diagrama de Contenedores

Este documento describe la arquitectura a nivel de contenedores (C4 Level 2) de la
**Plataforma de Gestión de Eventos**, un sistema distribuido basado en microservicios
que implementa patrones de arquitectura cloud-native como Event-Driven Architecture (EDA),
CQRS, Saga Orchestration y Arquitectura Hexagonal.

---

### Diagrama de Contenedores

```mermaid
graph TD
    classDef person fill:#08427B,color:#fff,stroke:#073B6F
    classDef service fill:#438DD5,color:#fff,stroke:#3C7FC0
    classDef infra fill:#85BBF0,color:#000,stroke:#78A8D8
    classDef bus fill:#F5A623,color:#000,stroke:#D4901E
    classDef queue fill:#7B68EE,color:#fff,stroke:#6A5ACD

    User["👤 Usuario<br/><i>Cliente / Organizador</i><br/>Interactúa vía REST API"]:::person

    subgraph Microservicios
        EVT["📦 Event Service<br/><i>Java 17 · Spring Boot 3</i><br/>Puerto 8080<br/>Arquitectura Hexagonal + DDD<br/>Ciclo de vida de eventos"]:::service
        BKG["📦 Booking Service<br/><i>Node.js · Express + TypeScript</i><br/>Puerto 3001<br/>CQRS + Arquitectura Hexagonal<br/>Reservas de entradas"]:::service
        PAY["📦 Payment Service<br/><i>Python · FastAPI</i><br/>Puerto 3002<br/>Saga Orchestration Pattern<br/>Transacciones distribuidas"]:::service
        NTF["📦 Notification Service<br/><i>Python · asyncio</i><br/>Sin puerto HTTP<br/>Event-Driven Consumer · SQS Polling<br/>Token Bucket Rate Limiting"]:::service
    end

    subgraph Infraestructura["Infraestructura AWS (LocalStack)"]
        PG[("🗄️ PostgreSQL (RDS)<br/>Base de datos<br/>Event Service")]:::infra
        DDB_B[("🗄️ DynamoDB<br/>Tabla: Bookings<br/>GSI: userId-index, eventId-index")]:::infra
        DDB_P[("🗄️ DynamoDB<br/>Tabla: payment-sagas")]:::infra
        EB{{"🔀 EventBridge<br/>Bus: event-management-bus"}}:::bus
        SQS["📬 SQS<br/>Cola: notification-queue"]:::queue
        DLQ["⚠️ SQS DLQ<br/>Cola: notification-dlq"]:::queue
    end

    %% Usuario → Servicios (REST)
    User -- "REST API" --> EVT
    User -- "REST API" --> BKG
    User -- "REST API" --> PAY

    %% Servicios → Bases de datos
    EVT -- "JDBC" --> PG
    BKG -- "AWS SDK" --> DDB_B
    PAY -- "AWS SDK" --> DDB_P

    %% Servicios → EventBridge (publicación de eventos)
    EVT -- "EventCreated<br/>EventPublished<br/>EventCancelled" --> EB
    BKG -- "BookingCreated<br/>BookingConfirmed<br/>BookingCancelled" --> EB
    PAY -- "PaymentConfirmed<br/>PaymentFailed" --> EB

    %% Saga: Payment → Booking (HTTP directo)
    PAY -- "HTTP: confirmar/cancelar<br/>reservas (Saga)" --> BKG

    %% EventBridge → SQS → Notification
    EB -- "Reglas de<br/>enrutamiento" --> SQS
    SQS -- "Polling<br/>asíncrono" --> NTF
    SQS -. "Mensajes fallidos" .-> DLQ

    %% Notification envía emails
    NTF -. "Email (mock provider)" .-> User
```

---

## Descripción de Componentes

### 1. Event Service — `Java 17 / Spring Boot 3` · Puerto 8080

| Aspecto | Detalle |
|---|---|
| **Patrón arquitectónico** | Arquitectura Hexagonal + Domain-Driven Design (DDD) |
| **Responsabilidad** | Gestionar el ciclo de vida completo de los eventos: creación, publicación y cancelación. |
| **Base de datos** | PostgreSQL (RDS) |
| **Eventos publicados** | `EventCreated`, `EventPublished`, `EventCancelled` → EventBridge |

### 2. Booking Service — `Node.js / Express + TypeScript` · Puerto 3001

| Aspecto | Detalle |
|---|---|
| **Patrón arquitectónico** | CQRS + Arquitectura Hexagonal |
| **Responsabilidad** | Gestionar las reservas de entradas para los eventos. |
| **Base de datos** | DynamoDB — Tabla `Bookings` con GSI `userId-index` y `eventId-index` |
| **Eventos publicados** | `BookingCreated`, `BookingConfirmed`, `BookingCancelled` → EventBridge |

### 3. Payment Service — `Python / FastAPI` · Puerto 3002

| Aspecto | Detalle |
|---|---|
| **Patrón arquitectónico** | Saga Orchestration Pattern |
| **Responsabilidad** | Orquestar transacciones distribuidas entre servicios. |
| **Pasos de la Saga** | `ReserveBooking` → `ProcessPayment` → `ConfirmBooking` |
| **Base de datos** | DynamoDB — Tabla `payment-sagas` |
| **Eventos publicados** | `PaymentConfirmed`, `PaymentFailed` → EventBridge |
| **Comunicación directa** | Llama a Booking Service vía HTTP para confirmar o cancelar reservas. |

### 4. Notification Service — `Python / asyncio` · Sin puerto HTTP

| Aspecto | Detalle |
|---|---|
| **Patrón arquitectónico** | Event-Driven Consumer (SQS Polling) |
| **Responsabilidad** | Consumir eventos desde SQS y enviar notificaciones por email (proveedor mock). |
| **Rate Limiting** | Token Bucket Algorithm |
| **Cola de entrada** | SQS `notification-queue` |
| **Cola de errores** | SQS DLQ `notification-dlq` |

---

## Infraestructura AWS (LocalStack)

| Recurso | Tipo | Descripción |
|---|---|---|
| PostgreSQL (RDS) | Base de datos relacional | Almacén persistente del Event Service. |
| DynamoDB `Bookings` | Base de datos NoSQL | Almacén del Booking Service con índices secundarios globales (`userId-index`, `eventId-index`). |
| DynamoDB `payment-sagas` | Base de datos NoSQL | Almacén de estado de sagas del Payment Service. |
| EventBridge `event-management-bus` | Bus de eventos | Bus central de eventos del dominio para comunicación asíncrona. |
| SQS `notification-queue` | Cola de mensajes | Cola que alimenta al Notification Service con eventos filtrados. |
| SQS `notification-dlq` | Cola de mensajes (DLQ) | Dead Letter Queue para mensajes que no pudieron ser procesados. |

---

## Patrones de Comunicación

### 🔁 Event-Driven Architecture (EDA)

Los microservicios se comunican de forma **asíncrona** a través de **Amazon EventBridge**.
Cada servicio publica eventos de dominio en el bus `event-management-bus`, y las reglas de
enrutamiento de EventBridge dirigen los eventos relevantes a la cola SQS `notification-queue`.

```
Servicio → EventBridge (bus) → Reglas → SQS → Notification Service
```

Este enfoque garantiza un **acoplamiento débil** entre productores y consumidores de eventos.

### 🔄 Saga Orchestration (Payment Service)

El **Payment Service** actúa como **orquestador** de una saga distribuida que coordina
la reserva y el pago de entradas. Los pasos son:

1. **ReserveBooking** — Solicita al Booking Service reservar entradas.
2. **ProcessPayment** — Procesa el pago internamente.
3. **ConfirmBooking** — Confirma la reserva en el Booking Service vía HTTP.

Si algún paso falla, el orquestador ejecuta las **compensaciones** correspondientes
(cancelar reserva, revertir pago) para mantener la consistencia eventual del sistema.

```
Payment Service --HTTP--> Booking Service (reservar)
Payment Service            (procesar pago)
Payment Service --HTTP--> Booking Service (confirmar / cancelar)
```

### 📖 CQRS — Command Query Responsibility Segregation (Booking Service)

El **Booking Service** implementa **CQRS** separando las operaciones de escritura (comandos)
de las operaciones de lectura (consultas). Esto permite optimizar cada ruta de forma
independiente y escalar las lecturas sin afectar las escrituras.

- **Comandos**: Crear reserva, confirmar reserva, cancelar reserva.
- **Consultas**: Listar reservas por usuario (`userId-index`), listar reservas por evento (`eventId-index`).

---

## Flujos de Comunicación — Resumen

| Origen | Destino | Protocolo | Descripción |
|---|---|---|---|
| Usuario | Event Service | REST / HTTP | Crear, publicar y cancelar eventos. |
| Usuario | Booking Service | REST / HTTP | Crear y consultar reservas. |
| Usuario | Payment Service | REST / HTTP | Iniciar pagos (saga). |
| Event Service | EventBridge | Evento async | `EventCreated`, `EventPublished`, `EventCancelled` |
| Booking Service | EventBridge | Evento async | `BookingCreated`, `BookingConfirmed`, `BookingCancelled` |
| Payment Service | EventBridge | Evento async | `PaymentConfirmed`, `PaymentFailed` |
| Payment Service | Booking Service | HTTP directo | Confirmar o cancelar reservas (pasos de la saga). |
| EventBridge | SQS `notification-queue` | Regla de enrutamiento | Filtrar y redirigir eventos relevantes. |
| SQS `notification-queue` | Notification Service | Polling (SQS) | Consumo asíncrono de eventos. |
| SQS `notification-queue` | SQS `notification-dlq` | Redrive policy | Mensajes que exceden los reintentos. |
| Notification Service | Usuario | Email (mock) | Envío de notificaciones. |
