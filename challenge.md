# Cloud-Native Architecture Challenge: Sistema de Gestión de Eventos

## Descripción General

Este caso de estudio está diseñado para demostrar la implementación práctica de múltiples patrones arquitectónicos en un sistema distribuido real. El proyecto simula una plataforma de gestión de eventos que permite crear eventos, gestionar reservas, procesar pagos y enviar notificaciones.

**Objetivo Educativo:** Implementar diferentes patrones arquitectónicos en distintos contextos para comprender cuándo y por qué usar cada uno.

## Patrones Arquitectónicos a Implementar

### 1. Hexagonal Architecture (Ports & Adapters)

- **Aplicado en:** Event Service y Booking Service
- **Objetivo:** Aislar la lógica de negocio de los detalles de infraestructura
- **Aprenderás:** Separación de capas, inversión de dependencias, testabilidad

### 2. CQRS (Command Query Responsibility Segregation)

- **Aplicado en:** Booking Service
- **Objetivo:** Separar operaciones de escritura y lectura para optimizar cada caso
- **Aprenderás:** Modelos de lectura vs escritura, eventual consistency, índices optimizados

### 3. Event-Driven Architecture (EDA)

- **Aplicado en:** Comunicación entre servicios
- **Objetivo:** Desacoplar servicios mediante eventos asíncronos
- **Aprenderás:** Event sourcing básico, pub/sub patterns, reactividad

### 4. Saga Pattern (Orchestration)

- **Aplicado en:** Payment Service
- **Objetivo:** Gestionar transacciones distribuidas con compensación
- **Aprenderás:** Transacciones distribuidas, rollback patterns, idempotencia

### 5. Buffer Pattern con SQS

- **Aplicado en:** Notification Service
- **Objetivo:** Desacoplar y absorber picos de carga
- **Aprenderás:** Rate limiting, backpressure, procesamiento asíncrono

## Arquitectura del Sistema

### Microservicios

#### 1. Event Service (Java + Spring Boot)
**Patrón Principal:** Hexagonal Architecture

**Responsabilidades:**
- Crear y publicar eventos (conciertos, conferencias, deportes)
- Gestionar información de venues y capacidad
- Consultar disponibilidad de eventos

**Bounded Context (DDD Simplificado):**
- **Aggregates:** Event, Venue
- **Value Objects:** EventDate, Capacity, Price, Location
- **Domain Events:** EventCreated, EventPublished, EventCancelled

**Tecnologías:**
- Base de datos: PostgreSQL (RDS en LocalStack)
- Mensajería: EventBridge
- API: REST

#### 2. Booking Service (TypeScript + Node.js)
**Patrones Principales:** Hexagonal Architecture + CQRS

**Responsabilidades:**
- Crear reservas de tickets
- Gestionar estados de reservas (pending, confirmed, cancelled)
- Consultar historial de reservas por usuario o evento

**CQRS Implementation:**
- **Write Model:** Commands para crear, confirmar y cancelar reservas
- **Read Model:** Queries optimizadas con índices GSI en DynamoDB
- **Eventual Consistency:** Sincronización entre modelos mediante eventos

**Bounded Context:**
- **Aggregates:** Booking, BookingItem
- **Value Objects:** BookingStatus, ReservationTime, TicketType
- **Domain Events:** BookingCreated, BookingConfirmed, BookingCancelled

**Tecnologías:**
- Base de datos: DynamoDB (write + read con GSI)
- Mensajería: EventBridge
- API: REST + GraphQL (opcional)

#### 3. Payment Service (Python + FastAPI)
**Patrón Principal:** Saga Pattern (Orchestration)

**Responsabilidades:**
- Orquestar el flujo de pago distribuido
- Coordinar reserva → pago → confirmación
- Implementar compensación en caso de fallo

**Saga Flow:**
1. Reserve Booking (Booking Service)
2. Process Payment (Mock Payment Gateway)
3. Confirm Booking (Booking Service)
4. Send Notification (Notification Service)

**Compensation Flow:**
- Payment Failed → Release Booking
- Booking Unavailable → Refund Payment

**Tecnologías:**
- Base de datos: DynamoDB (saga state machine)
- Mensajería: EventBridge + SQS
- API: REST

#### 4. Notification Service (Python + FastAPI)
**Patrón Principal:** Buffer Pattern con SQS

**Responsabilidades:**
- Procesar notificaciones de forma asíncrona
- Enviar confirmaciones de reserva por email
- Enviar recordatorios de eventos

**Buffer Implementation:**
- **SQS Queue:** Absorbe picos de notificaciones
- **Dead Letter Queue (DLQ):** Manejo de fallos
- **Batch Processing:** Procesa múltiples mensajes en lote
- **Rate Limiting:** Controla tasa de envío para evitar throttling

**Tecnologías:**
- Queue: SQS + DLQ
- Procesamiento: Lambda (polling SQS)
- Mock: Simular envío de emails con logs

## Flujos de Negocio

### Flujo 1: Crear Evento
**Patrón:** Event-Driven Architecture

1. Admin crea evento en Event Service
2. Event Service publica EventCreated a EventBridge
3. Booking Service escucha evento y crea índices de disponibilidad
4. Analytics Service (opcional) registra evento para métricas

### Flujo 2: Reservar Tickets (Happy Path)
**Patrón:** Saga Pattern + CQRS

1. Usuario solicita reserva en Booking Service (Command)
2. Booking Service crea reserva en estado PENDING
3. Booking Service publica BookingCreated a EventBridge
4. Payment Service inicia Saga:
   - Llama a Payment Gateway (mock)
   - Si éxito: envía comando ConfirmBooking
   - Si fallo: envía comando CancelBooking
5. Booking Service actualiza estado a CONFIRMED
6. Booking Service publica BookingConfirmed
7. Notification Service recibe evento en SQS
8. Lambda procesa cola y envía email de confirmación

### Flujo 3: Reservar Tickets (Failure Path)
**Patrón:** Saga Compensation

1. Usuario solicita reserva
2. Booking Service crea reserva PENDING
3. Payment Service inicia Saga
4. Payment Gateway falla (tarjeta rechazada)
5. Payment Service ejecuta compensación:
   - Envía comando CancelBooking
   - Registra intento fallido
6. Booking Service libera reserva
7. Notification Service envía email de fallo

### Flujo 4: Consultar Reservas
**Patrón:** CQRS Read Model

1. Usuario consulta sus reservas
2. Booking Service usa Read Model (GSI en DynamoDB)
3. Retorna lista optimizada sin joins complejos
4. Datos pueden estar ligeramente desactualizados (eventual consistency)

## Stack Tecnológico

### Lenguajes
- Java 17+ (Event Service)
- TypeScript/Node.js 20+ (Booking Service)
- Python 3.11+ (Payment Service, Notification Service)

### AWS Services (LocalStack)
- **Compute:** Lambda
- **Storage:** DynamoDB, RDS (PostgreSQL)
- **Messaging:** EventBridge, SQS, SNS
- **API:** API Gateway
- **Monitoring:** CloudWatch Logs

### Herramientas de Desarrollo
- LocalStack: Emulación local de AWS
- Docker Compose: Orquestación de servicios
- AWS CLI: Interacción con LocalStack
- Terraform/CDK: Infrastructure as Code (opcional)

## Configuración del Entorno

### Requisitos Previos
- Docker Desktop instalado
- AWS CLI configurado
- Node.js 20+, Python 3.11+, Java 17+
- LocalStack CLI (opcional pero recomendado)

### LocalStack Setup

LocalStack permite ejecutar servicios AWS localmente sin costos ni cuenta de AWS. Soporta más de 90 servicios en su versión gratuita.

**Servicios LocalStack Utilizados:**
- ✓ DynamoDB (Free)
- ✓ SQS (Free)
- ✓ SNS (Free)
- ✓ EventBridge (Free)
- ✓ Lambda (Free)
- ✓ API Gateway (Free)
- ✓ RDS PostgreSQL (Free)
- ✓ CloudWatch Logs (Free)

**Configuración Básica:**

```yaml
# docker-compose.yml
services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=dynamodb,sqs,sns,events,lambda,apigateway,rds,logs
      - DEBUG=1
    volumes:
      - "./localstack-data:/var/lib/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"
```

**Endpoint Local:**
- Todos los servicios: http://localhost:4566

## Conceptos DDD Simplificados

### Bounded Contexts
Cada microservicio representa un bounded context:
- **Event Context:** Todo relacionado con eventos y venues
- **Booking Context:** Reservas y tickets
- **Payment Context:** Pagos y transacciones
- **Notification Context:** Comunicaciones con usuarios

### Aggregates
Entidades raíz que garantizan consistencia:
- **Event Aggregate:** Event + Venue
- **Booking Aggregate:** Booking + BookingItems
- **Payment Aggregate:** Payment + PaymentAttempts

### Domain Events
Eventos de negocio que comunican cambios:
- EventCreated, EventPublished
- BookingCreated, BookingConfirmed, BookingCancelled
- PaymentProcessed, PaymentFailed
- NotificationSent

## Objetivos de Aprendizaje

### Nivel 1: Fundamentos
- [ ] Configurar LocalStack y servicios básicos
- [ ] Implementar un servicio con Hexagonal Architecture
- [ ] Crear y consumir eventos en EventBridge
- [ ] Usar DynamoDB con índices GSI

### Nivel 2: Patrones Intermedios
- [ ] Implementar CQRS con modelos separados
- [ ] Crear una Saga con compensación
- [ ] Configurar SQS con DLQ
- [ ] Implementar Lambda para procesamiento asíncrono

### Nivel 3: Integración Completa
- [ ] Orquestar flujo completo de reserva
- [ ] Implementar manejo de errores distribuidos
- [ ] Agregar observabilidad con CloudWatch
- [ ] Optimizar consultas con índices

## Referencias y Recursos

### Patrones Arquitectónicos
- **Hexagonal Architecture:** "Ports and Adapters" by Alistair Cockburn
- **CQRS:** Martin Fowler - CQRS Pattern
- **Saga Pattern:** Chris Richardson - Microservices Patterns
- **Event-Driven Architecture:** "Building Event-Driven Microservices" by Adam Bellemare

### LocalStack
- Documentación Oficial: https://docs.localstack.cloud/
- Servicios Soportados: https://docs.localstack.cloud/aws/services/
- Getting Started: https://docs.localstack.cloud/getting-started/
- GitHub: https://github.com/localstack/localstack

### AWS Services
- **DynamoDB:** Guía de diseño de tablas y GSI
- **EventBridge:** Event-driven patterns
- **SQS:** Queue patterns y DLQ
- **Lambda:** Serverless best practices

### Domain-Driven Design
- "Domain-Driven Design Distilled" by Vaughn Vernon (versión simplificada)
- Bounded Contexts: Martin Fowler's blog
- Aggregates: DDD Reference by Eric Evans

## Estrategia de Implementación

### Fase 1: Setup (Semana 1)
1. Configurar LocalStack con Docker Compose
2. Crear infraestructura básica (DynamoDB, SQS, EventBridge)
3. Implementar Event Service con Hexagonal Architecture
4. Probar creación de eventos y publicación a EventBridge

### Fase 2: CQRS (Semana 2)
1. Implementar Booking Service con separación Command/Query
2. Configurar DynamoDB con GSI para read model
3. Crear endpoints REST para commands y queries
4. Probar eventual consistency entre modelos

### Fase 3: Saga Pattern (Semana 3)
1. Implementar Payment Service como orquestador
2. Crear state machine para flujo de pago
3. Implementar compensación para fallos
4. Probar happy path y failure scenarios

### Fase 4: Buffer Pattern (Semana 4)
1. Implementar Notification Service con SQS
2. Configurar Lambda para polling de cola
3. Agregar DLQ para mensajes fallidos
4. Probar procesamiento en lote y rate limiting

### Fase 5: Integración (Semana 5)
1. Conectar todos los servicios
2. Implementar flujo end-to-end
3. Agregar observabilidad y logs
4. Documentar arquitectura con diagramas C4

## Entregables del Proyecto

### Documentación
- [ ] Diagrama de arquitectura (C4 Model)
- [ ] Diagramas de secuencia para flujos principales
- [ ] README con instrucciones de setup
- [ ] Decisiones arquitectónicas (ADRs)

### Código
- [ ] 4 microservicios funcionales
- [ ] Tests unitarios para lógica de dominio
- [ ] Tests de integración con LocalStack
- [ ] Scripts de infraestructura (Terraform/CDK opcional)

### Demo
- [ ] Docker Compose para levantar todo el sistema
- [ ] Colección Postman/Insomnia con requests de ejemplo
- [ ] Datos de prueba (seed scripts)
- [ ] Video demo de 5-10 minutos (opcional)

## Consejos para el Desarrollo

### Usa Cursor AI Efectivamente
- Genera boilerplate de Hexagonal Architecture
- Pide implementaciones de patrones específicos
- Solicita tests unitarios automáticamente
- Usa para refactoring y optimización

### Debugging con LocalStack
- Usa awslocal CLI para interactuar con servicios
- Revisa logs de LocalStack para troubleshooting
- Usa LocalStack Web UI para visualizar recursos
- Configura CloudWatch Logs para observabilidad

### Testing Strategy
- **Unit Tests:** Lógica de dominio aislada
- **Integration Tests:** Servicios + LocalStack
- **Contract Tests:** APIs entre servicios
- **E2E Tests:** Flujos completos (opcional)

### Iteración Incremental
- Implementa un patrón a la vez
- Valida cada componente antes de integrar
- Refactoriza continuamente
- Documenta decisiones importantes

## Criterios de Éxito

### Técnicos
- ✓ Todos los servicios corren en LocalStack
- ✓ Cada patrón está correctamente implementado
- ✓ Flujo end-to-end funciona sin errores
- ✓ Tests tienen >70% de cobertura

### Arquitectónicos
- ✓ Separación clara de responsabilidades
- ✓ Bajo acoplamiento entre servicios
- ✓ Alta cohesión dentro de cada servicio
- ✓ Manejo robusto de errores

### Profesionales
- ✓ Código limpio y bien documentado
- ✓ Commits atómicos con mensajes claros
- ✓ README profesional con instrucciones
- ✓ Proyecto presentable en portfolio

## Próximos Pasos

1. **Fork/Clone:** Crea tu repositorio del proyecto
2. **Setup:** Configura LocalStack y entorno de desarrollo
3. **Plan:** Define tu roadmap de implementación
4. **Build:** Implementa servicio por servicio
5. **Test:** Valida cada componente
6. **Document:** Crea diagramas y documentación
7. **Demo:** Prepara presentación del proyecto

## Soporte y Comunidad

- **LocalStack Slack:** Comunidad activa para dudas
- **GitHub Issues:** Reporta problemas con LocalStack
- **Stack Overflow:** Tag localstack para preguntas
- **AWS Documentation:** Referencia oficial de servicios

**¡Buena suerte con tu proyecto!** Este caso de estudio te dará experiencia práctica con patrones arquitectónicos modernos que son altamente valorados en la industria.
