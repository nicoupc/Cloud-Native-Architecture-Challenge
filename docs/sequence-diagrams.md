# Diagramas de Secuencia — Plataforma de Gestión de Eventos Cloud-Native

Este documento describe los flujos principales de la plataforma mediante diagramas de secuencia Mermaid. La arquitectura se basa en **Event-Driven Architecture (EDA)**, el patrón **Saga** para transacciones distribuidas y **CQRS** para separar lecturas de escrituras.

---

## Flujo 1: Crear y Publicar Evento

Este flujo ilustra el ciclo de vida de un evento, desde su creación en estado borrador hasta su publicación. Demuestra el patrón **Event-Driven Architecture (EDA)**: cada cambio de estado genera un evento de dominio que se propaga a través de EventBridge, permitiendo que otros servicios reaccionen de forma desacoplada.

```mermaid
sequenceDiagram
    participant User as Cliente
    participant EventService as Event Service<br/>(Java :8080)
    participant PostgreSQL as Event DB<br/>(PostgreSQL)
    participant EventBridge as AWS EventBridge
    participant SQS as notification-queue<br/>(SQS)
    participant NotificationService as Notification Service<br/>(Python - SQS Consumer)

    Note over User,NotificationService: Fase 1 — Creación del evento

    User->>EventService: POST /api/v1/events<br/>(name, description, type, date, capacity, price)
    EventService->>PostgreSQL: Guardar evento (status=DRAFT)
    EventService->>EventBridge: Publicar evento EventCreated
    EventService-->>User: 201 Created (datos del evento)

    Note over User,NotificationService: Fase 2 — Publicación del evento

    User->>EventService: POST /api/v1/events/{id}/publish
    EventService->>PostgreSQL: Actualizar status=PUBLISHED
    EventService->>EventBridge: Publicar evento EventPublished
    EventBridge->>SQS: Enrutar EventPublished a notification-queue
    SQS->>NotificationService: Poll del mensaje
    NotificationService->>NotificationService: Enviar notificación por email
    EventService-->>User: 200 OK (evento publicado)
```

> **Decisiones arquitectónicas clave:**
> - **EDA (Event-Driven Architecture):** Cada cambio de estado emite un evento de dominio, permitiendo acoplamiento débil entre servicios.
> - **Estado DRAFT → PUBLISHED:** El ciclo de vida en dos fases permite validar el evento antes de hacerlo visible.
> - **EventBridge como bus central:** Actúa como intermediario, enrutando eventos a las colas correspondientes mediante reglas declarativas.

---

## Flujo 2: Reservar Tickets — Happy Path

Este flujo muestra el camino exitoso de una reserva de tickets, orquestado por el **patrón Saga**. El Payment Service actúa como orquestador, coordinando los pasos de reserva, procesamiento de pago y confirmación de forma secuencial. Al completarse, se emite un evento de dominio que dispara la notificación al usuario.

```mermaid
sequenceDiagram
    participant User as Cliente
    participant BookingService as Booking Service<br/>(Node.js :3001)
    participant DynamoDB_B as Bookings Table<br/>(DynamoDB)
    participant PaymentService as Payment Service<br/>(Python :3002)
    participant DynamoDB_P as payment-sagas Table<br/>(DynamoDB)
    participant EventBridge as AWS EventBridge
    participant SQS as notification-queue<br/>(SQS)
    participant NotificationService as Notification Service<br/>(Python - SQS Consumer)

    Note over User,NotificationService: Fase 1 — Crear la reserva

    User->>BookingService: POST /api/v1/bookings<br/>(userId, eventId, ticketQuantity, pricePerTicket)
    BookingService->>DynamoDB_B: Guardar reserva (status=PENDING)
    BookingService->>EventBridge: Publicar evento BookingCreated
    BookingService-->>User: 201 Created (datos de la reserva)

    Note over User,NotificationService: Fase 2 — Orquestación de la Saga de Pago

    User->>PaymentService: POST /api/v1/sagas<br/>(booking_id, amount, currency)
    PaymentService->>DynamoDB_P: Crear saga (status=RUNNING)
    PaymentService->>PaymentService: Step 1 — RESERVE_BOOKING (interno)
    PaymentService->>PaymentService: Step 2 — PROCESS_PAYMENT (validar pago)
    PaymentService->>BookingService: POST /api/v1/bookings/{id}/confirm<br/>(Step 3 — CONFIRM_BOOKING)
    BookingService->>DynamoDB_B: Actualizar status=CONFIRMED
    BookingService-->>PaymentService: 200 OK (confirmada)
    PaymentService->>DynamoDB_P: Actualizar saga status=COMPLETED

    Note over User,NotificationService: Fase 3 — Notificación asíncrona

    PaymentService->>EventBridge: Publicar evento PaymentConfirmed
    EventBridge->>SQS: Enrutar PaymentConfirmed a notification-queue
    SQS->>NotificationService: Poll del mensaje
    NotificationService->>NotificationService: Enviar email de confirmación
    PaymentService-->>User: 201 Created (datos de la saga)
```

> **Decisiones arquitectónicas clave:**
> - **Patrón Saga (orquestado):** El Payment Service coordina los pasos secuenciales, garantizando consistencia eventual entre servicios.
> - **Separación de responsabilidades:** El Booking Service gestiona el estado de la reserva; el Payment Service orquesta la transacción distribuida.
> - **Notificación desacoplada:** La confirmación al usuario se envía de forma asíncrona vía EventBridge → SQS → Notification Service.

---

## Flujo 3: Reservar Tickets — Failure Path (Compensación)

Este flujo muestra qué sucede cuando el procesamiento de pago falla. El **patrón Saga** ejecuta acciones de compensación en orden inverso para revertir los cambios parciales, garantizando la **consistencia eventual** del sistema. Este es un ejemplo clásico de gestión de fallos en arquitecturas distribuidas.

```mermaid
sequenceDiagram
    participant User as Cliente
    participant PaymentService as Payment Service<br/>(Python :3002)
    participant DynamoDB_P as payment-sagas Table<br/>(DynamoDB)
    participant BookingService as Booking Service<br/>(Node.js :3001)
    participant DynamoDB_B as Bookings Table<br/>(DynamoDB)
    participant EventBridge as AWS EventBridge
    participant SQS as notification-queue<br/>(SQS)
    participant NotificationService as Notification Service<br/>(Python - SQS Consumer)

    Note over User,NotificationService: Fase 1 — Ejecución de la Saga (fallo en el pago)

    User->>PaymentService: POST /api/v1/sagas<br/>(booking_id, amount, currency)
    PaymentService->>DynamoDB_P: Crear saga (status=RUNNING)
    PaymentService->>PaymentService: Step 1 — RESERVE_BOOKING
    PaymentService->>PaymentService: Step 2 — PROCESS_PAYMENT → FALLA

    Note over User,NotificationService: Fase 2 — Compensación (rollback distribuido)

    PaymentService->>DynamoDB_P: Actualizar saga status=COMPENSATING
    PaymentService->>PaymentService: Compensar Step 1 (cancelar reserva)
    PaymentService->>BookingService: POST /api/v1/bookings/{id}/cancel
    BookingService->>DynamoDB_B: Actualizar status=CANCELLED
    PaymentService->>DynamoDB_P: Actualizar saga status=COMPENSATED

    Note over User,NotificationService: Fase 3 — Notificación de fallo

    PaymentService->>EventBridge: Publicar evento PaymentFailed
    EventBridge->>SQS: Enrutar PaymentFailed a notification-queue
    SQS->>NotificationService: Poll del mensaje
    NotificationService->>NotificationService: Enviar email de notificación de fallo
    PaymentService-->>User: 200 OK (datos de la saga con status fallido)
```

> **Decisiones arquitectónicas clave:**
> - **Compensación en orden inverso:** Si un paso falla, la saga deshace los pasos anteriores ejecutando las acciones compensatorias correspondientes.
> - **Estado COMPENSATING → COMPENSATED:** La saga registra cada fase de la compensación, permitiendo trazabilidad y recuperación ante fallos parciales.
> - **Notificación de fallo:** El usuario es notificado de forma asíncrona a través del mismo mecanismo de eventos, manteniendo la consistencia del flujo.

---

## Flujo 4: Consultar Reservas (CQRS Read)

Este flujo muestra el lado de **lectura** del patrón **CQRS (Command Query Responsibility Segregation)**. Las consultas se realizan directamente contra DynamoDB utilizando índices secundarios globales (GSI) optimizados para cada patrón de acceso, sin pasar por la lógica de escritura ni por el bus de eventos.

```mermaid
sequenceDiagram
    participant User as Cliente
    participant BookingService as Booking Service<br/>(Node.js :3001)
    participant DynamoDB_B as Bookings Table<br/>(DynamoDB)

    Note over User,DynamoDB_B: Consulta 1 — Obtener reserva por ID

    User->>BookingService: GET /api/v1/bookings/{id}
    BookingService->>DynamoDB_B: Query por clave primaria (bookingId)
    DynamoDB_B-->>BookingService: Datos de la reserva
    BookingService-->>User: 200 OK (datos de la reserva)

    Note over User,DynamoDB_B: Consulta 2 — Obtener reservas por usuario

    User->>BookingService: GET /api/v1/bookings/user/{userId}
    BookingService->>DynamoDB_B: Query por GSI userId-index
    DynamoDB_B-->>BookingService: Lista de reservas del usuario
    BookingService-->>User: 200 OK (array de reservas)

    Note over User,DynamoDB_B: Consulta 3 — Obtener reservas por evento

    User->>BookingService: GET /api/v1/bookings/event/{eventId}
    BookingService->>DynamoDB_B: Query por GSI eventId-index
    DynamoDB_B-->>BookingService: Lista de reservas del evento
    BookingService-->>User: 200 OK (array de reservas)
```

> **Decisiones arquitectónicas clave:**
> - **CQRS:** Las operaciones de lectura están completamente separadas de las de escritura, permitiendo optimizar cada lado de forma independiente.
> - **DynamoDB con GSI:** Los índices secundarios globales (`userId-index`, `eventId-index`) permiten consultas eficientes por diferentes patrones de acceso sin duplicar datos.
> - **Lecturas directas sin eventos:** A diferencia de los flujos de escritura, las consultas no generan eventos de dominio, reduciendo la latencia y la complejidad.
