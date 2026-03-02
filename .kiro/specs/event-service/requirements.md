# Requirements Document

## Introduction

El Event Service es el primer microservicio del sistema de gestión de eventos. Su responsabilidad principal es gestionar el ciclo de vida completo de eventos (conciertos, conferencias, deportes) y sus venues (lugares), así como publicar eventos de dominio para que otros servicios puedan reaccionar a los cambios. Este servicio implementa Hexagonal Architecture para mantener el dominio aislado de los detalles de infraestructura.

## Glossary

- **Event_Service**: El microservicio responsable de gestionar eventos y venues
- **Event**: Un agregado de dominio que representa un evento (concierto, conferencia, deporte) con fecha, venue, capacidad y precio
- **Venue**: Un agregado de dominio que representa un lugar físico donde ocurren eventos, con ubicación y capacidad máxima
- **Event_Repository**: Puerto de salida para persistir y recuperar eventos
- **Venue_Repository**: Puerto de salida para persistir y recuperar venues
- **Event_Publisher**: Puerto de salida para publicar eventos de dominio a EventBridge
- **Postgres_Adapter**: Adaptador de infraestructura que implementa los repositorios usando PostgreSQL
- **EventBridge_Adapter**: Adaptador de infraestructura que implementa el publicador usando AWS EventBridge
- **REST_Controller**: Adaptador de entrada que expone endpoints HTTP
- **Available_Capacity**: La cantidad de tickets disponibles para un evento (capacidad total menos reservas)
- **Event_Status**: El estado de un evento (DRAFT, PUBLISHED, CANCELLED)

## Requirements

### Requirement 1: Create Events

**User Story:** As an event administrator, I want to create new events with venue, date, capacity and pricing information, so that users can discover and book tickets for events.

#### Acceptance Criteria

1. WHEN a valid event creation request is received, THE Event_Service SHALL create an Event with unique identifier, name, description, event type, venue reference, event date, total capacity, available capacity, and price
2. WHEN an Event is created, THE Event_Service SHALL set the Event_Status to DRAFT
3. WHEN an Event is created, THE Event_Service SHALL set Available_Capacity equal to total capacity
4. IF the venue reference does not exist, THEN THE Event_Service SHALL return an error indicating invalid venue
5. IF the event date is in the past, THEN THE Event_Service SHALL return an error indicating invalid date
6. IF the total capacity exceeds the Venue maximum capacity, THEN THE Event_Service SHALL return an error indicating capacity limit exceeded
7. IF the price is negative, THEN THE Event_Service SHALL return an error indicating invalid price
8. WHEN an Event is successfully created, THE Event_Service SHALL return the Event with HTTP status 201

### Requirement 2: Publish Events

**User Story:** As an event administrator, I want to publish events to make them available for booking, so that users can purchase tickets.

#### Acceptance Criteria

1. WHEN a publish request is received for an Event in DRAFT status, THE Event_Service SHALL change the Event_Status to PUBLISHED
2. WHEN an Event transitions to PUBLISHED status, THE Event_Service SHALL publish an EventCreated domain event to EventBridge
3. THE EventCreated domain event SHALL contain event identifier, name, venue identifier, event date, available capacity, and price
4. IF a publish request is received for an Event not in DRAFT status, THEN THE Event_Service SHALL return an error indicating invalid state transition
5. IF the EventBridge_Adapter fails to publish the domain event, THEN THE Event_Service SHALL rollback the status change and return an error

### Requirement 3: List Events

**User Story:** As a user, I want to browse available events, so that I can find events I'm interested in attending.

#### Acceptance Criteria

1. WHEN a list events request is received, THE Event_Service SHALL return all Events with PUBLISHED status
2. THE Event_Service SHALL support filtering by event type (concert, conference, sports)
3. THE Event_Service SHALL support filtering by date range
4. THE Event_Service SHALL return events ordered by event date in ascending order
5. WHEN no events match the filter criteria, THE Event_Service SHALL return an empty list with HTTP status 200

### Requirement 4: Retrieve Event Details

**User Story:** As a user, I want to view detailed information about a specific event, so that I can decide whether to book tickets.

#### Acceptance Criteria

1. WHEN a valid event identifier is provided, THE Event_Service SHALL return the Event with all details including venue information
2. IF the event identifier does not exist, THEN THE Event_Service SHALL return an error with HTTP status 404
3. THE Event_Service SHALL include the associated Venue details (name, location, maximum capacity) in the response

### Requirement 5: Check Event Availability

**User Story:** As a user, I want to check ticket availability for an event, so that I know if I can book tickets.

#### Acceptance Criteria

1. WHEN an availability check request is received for a valid event identifier, THE Event_Service SHALL return the Available_Capacity
2. THE Event_Service SHALL return the total capacity and Available_Capacity in the response
3. IF the event identifier does not exist, THEN THE Event_Service SHALL return an error with HTTP status 404
4. WHEN Available_Capacity is zero, THE Event_Service SHALL include a sold_out flag set to true in the response

### Requirement 6: Update Events

**User Story:** As an event administrator, I want to update event information, so that I can correct mistakes or adjust event details.

#### Acceptance Criteria

1. WHEN a valid update request is received for an Event in DRAFT status, THE Event_Service SHALL update the modifiable fields (name, description, price)
2. THE Event_Service SHALL NOT allow modification of event date, venue, or total capacity after creation
3. IF an update request is received for an Event in PUBLISHED status, THEN THE Event_Service SHALL only allow updates to description and price
4. IF an update request is received for an Event in CANCELLED status, THEN THE Event_Service SHALL return an error indicating the event cannot be modified
5. WHEN an Event in PUBLISHED status is updated, THE Event_Service SHALL publish an EventUpdated domain event to EventBridge

### Requirement 7: Cancel Events

**User Story:** As an event administrator, I want to cancel events, so that I can handle situations where events cannot proceed.

#### Acceptance Criteria

1. WHEN a cancel request is received for an Event in DRAFT or PUBLISHED status, THE Event_Service SHALL change the Event_Status to CANCELLED
2. WHEN an Event transitions to CANCELLED status, THE Event_Service SHALL publish an EventCancelled domain event to EventBridge
3. THE EventCancelled domain event SHALL contain event identifier and cancellation timestamp
4. IF a cancel request is received for an Event already in CANCELLED status, THEN THE Event_Service SHALL return an error indicating the event is already cancelled
5. THE Event_Service SHALL preserve all event data when cancelling (no deletion)

### Requirement 8: Manage Venues

**User Story:** As an event administrator, I want to create and manage venues, so that I can associate events with physical locations.

#### Acceptance Criteria

1. WHEN a valid venue creation request is received, THE Event_Service SHALL create a Venue with unique identifier, name, location (address, city, country), and maximum capacity
2. IF the maximum capacity is less than or equal to zero, THEN THE Event_Service SHALL return an error indicating invalid capacity
3. WHEN a venue list request is received, THE Event_Service SHALL return all Venues ordered by name
4. WHEN a valid venue identifier is provided, THE Event_Service SHALL return the Venue details
5. IF a venue identifier does not exist, THEN THE Event_Service SHALL return an error with HTTP status 404

### Requirement 9: Persist Data

**User Story:** As the system, I want to persist events and venues reliably, so that data is not lost and can be recovered.

#### Acceptance Criteria

1. THE Postgres_Adapter SHALL store Events in a PostgreSQL database table with all event attributes
2. THE Postgres_Adapter SHALL store Venues in a PostgreSQL database table with all venue attributes
3. THE Postgres_Adapter SHALL use database transactions to ensure data consistency
4. IF a database operation fails, THEN THE Postgres_Adapter SHALL rollback the transaction and propagate the error
5. THE Postgres_Adapter SHALL create appropriate indexes on event_date and event_status columns for query performance

### Requirement 10: Hexagonal Architecture Compliance

**User Story:** As a developer, I want the service to follow Hexagonal Architecture principles, so that the domain logic is isolated and testable.

#### Acceptance Criteria

1. THE Event_Service SHALL organize code into three layers: domain, application, and infrastructure
2. THE domain layer SHALL contain only business logic with no dependencies on frameworks or infrastructure
3. THE domain layer SHALL define ports (interfaces) for Event_Repository, Venue_Repository, and Event_Publisher
4. THE infrastructure layer SHALL implement adapters for the ports (Postgres_Adapter, EventBridge_Adapter, REST_Controller)
5. THE application layer SHALL orchestrate use cases by calling domain services and ports
6. FOR ALL domain entities and value objects, the domain layer SHALL enforce invariants and business rules
7. THE REST_Controller SHALL translate HTTP requests to domain commands and domain responses to HTTP responses

### Requirement 11: Event Domain Event Publishing

**User Story:** As the system, I want to publish domain events to EventBridge, so that other services can react to event lifecycle changes.

#### Acceptance Criteria

1. WHEN an Event transitions to PUBLISHED status, THE EventBridge_Adapter SHALL publish an EventCreated event with schema version, event identifier, name, venue identifier, event date, available capacity, and price
2. WHEN an Event in PUBLISHED status is updated, THE EventBridge_Adapter SHALL publish an EventUpdated event with event identifier and updated fields
3. WHEN an Event transitions to CANCELLED status, THE EventBridge_Adapter SHALL publish an EventCancelled event with event identifier and cancellation timestamp
4. THE EventBridge_Adapter SHALL publish events to the event bus named "event-management-bus"
5. THE EventBridge_Adapter SHALL include event source as "event-service" in all published events
6. IF EventBridge publishing fails after 3 retry attempts, THEN THE EventBridge_Adapter SHALL log the failure and propagate the error

### Requirement 12: Input Validation

**User Story:** As the system, I want to validate all inputs, so that invalid data does not corrupt the system state.

#### Acceptance Criteria

1. WHEN an event creation request is received, THE Event_Service SHALL validate that name is not empty and has maximum length of 200 characters
2. WHEN an event creation request is received, THE Event_Service SHALL validate that description has maximum length of 2000 characters
3. WHEN an event creation request is received, THE Event_Service SHALL validate that event type is one of: CONCERT, CONFERENCE, SPORTS
4. WHEN a venue creation request is received, THE Event_Service SHALL validate that name is not empty and has maximum length of 200 characters
5. WHEN a venue creation request is received, THE Event_Service SHALL validate that address, city, and country are not empty
6. IF any validation fails, THEN THE Event_Service SHALL return an error with HTTP status 400 and descriptive error message

### Requirement 13: Error Handling

**User Story:** As a developer, I want consistent error handling, so that I can diagnose and fix issues quickly.

#### Acceptance Criteria

1. WHEN a domain rule violation occurs, THE Event_Service SHALL return an error response with HTTP status 400 and error code
2. WHEN a resource is not found, THE Event_Service SHALL return an error response with HTTP status 404
3. WHEN a database error occurs, THE Event_Service SHALL return an error response with HTTP status 500 and log the full error details
4. WHEN an EventBridge publishing error occurs, THE Event_Service SHALL return an error response with HTTP status 500 and log the full error details
5. THE Event_Service SHALL include a correlation identifier in all error responses for tracing
6. THE Event_Service SHALL NOT expose internal implementation details or stack traces in error responses

### Requirement 14: LocalStack Integration

**User Story:** As a developer, I want the service to work with LocalStack, so that I can develop and test locally without AWS costs.

#### Acceptance Criteria

1. WHEN running in local development mode, THE Event_Service SHALL connect to PostgreSQL at the LocalStack RDS endpoint
2. WHEN running in local development mode, THE EventBridge_Adapter SHALL publish events to LocalStack EventBridge at http://localhost:4566
3. THE Event_Service SHALL read AWS endpoint configuration from environment variables
4. THE Event_Service SHALL use AWS region "us-east-1" for all AWS service calls
5. THE Event_Service SHALL create database schema automatically on startup if it does not exist
