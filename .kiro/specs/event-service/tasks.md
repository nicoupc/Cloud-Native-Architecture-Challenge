# Implementation Plan: Event Service

## Overview

This plan implements the Event Service using Hexagonal Architecture with Java 17+ and Spring Boot. The implementation follows a bottom-up approach: domain layer first (pure business logic), then application layer (use cases), and finally infrastructure layer (adapters). Each task builds incrementally, with checkpoints to validate progress.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create Maven project with Spring Boot 3.x parent
  - Configure dependencies: Spring Data JPA, PostgreSQL driver, AWS SDK for EventBridge, Flyway, validation
  - Add test dependencies: JUnit 5, Mockito, AssertJ, jqwik, Testcontainers
  - Create package structure following hexagonal architecture (domain, application, infrastructure)
  - _Requirements: 10.1, 10.2, 14.3_

- [ ] 2. Implement domain layer - Value Objects
  - [ ] 2.1 Create value objects with validation
    - Implement EventId, VenueId (UUID wrappers)
    - Implement EventDate with future date validation
    - Implement Capacity with non-negative constraint
    - Implement Price with non-negative amount and currency
    - Implement Location with address, city, country
    - Create EventType enum (CONCERT, CONFERENCE, SPORTS)
    - Create EventStatus enum (DRAFT, PUBLISHED, CANCELLED)
    - _Requirements: 1.5, 1.6, 1.7, 8.2, 10.6, 12.3_

  - [ ]* 2.2 Write property test for value object validation
    - **Property 8: Negative Price Rejection**
    - **Property 25: Invalid Venue Capacity Rejection**
    - **Validates: Requirements 1.7, 8.2**

- [ ] 3. Implement domain layer - Domain Events
  - [ ] 3.1 Create domain event interfaces and records
    - Create sealed DomainEvent interface
    - Implement EventCreated record with event details
    - Implement EventUpdated record with changed fields map
    - Implement EventCancelled record with timestamp
    - _Requirements: 2.2, 2.3, 6.5, 7.2, 7.3, 11.1, 11.2, 11.3_

- [ ] 4. Implement domain layer - Aggregates
  - [ ] 4.1 Implement Venue aggregate
    - Create Venue class with id, name, location, maxCapacity
    - Add canAccommodate(Capacity) business method
    - Enforce invariants: positive capacity, non-empty name
    - _Requirements: 8.1, 8.2, 10.6_

  - [ ] 4.2 Implement Event aggregate
    - Create Event class with all attributes (id, name, description, type, venueId, eventDate, capacities, price, status)
    - Implement static create() factory method setting DRAFT status and initial capacity
    - Add publish() method for DRAFT → PUBLISHED transition
    - Add cancel() method for DRAFT/PUBLISHED → CANCELLED transition
    - Add updateDetails() method with status-based restrictions
    - Enforce all invariants: capacity limits, status transitions, date validation
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 6.1, 6.2, 6.3, 6.4, 7.1, 10.6_

  - [ ]* 4.3 Write property tests for Event aggregate
    - **Property 1: Event Creation Completeness**
    - **Property 2: New Events Start in DRAFT Status**
    - **Property 3: Initial Capacity Invariant**
    - **Property 6: Past Date Rejection**
    - **Property 7: Capacity Limit Enforcement**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.5, 1.6**

  - [ ]* 4.4 Write unit tests for Event state transitions
    - Test DRAFT → PUBLISHED transition
    - Test invalid state transitions (non-DRAFT publish, already cancelled)
    - Test update permissions by status (DRAFT allows all, PUBLISHED restricted, CANCELLED blocked)
    - _Requirements: 2.1, 2.4, 6.1, 6.3, 6.4, 7.4_

- [ ] 5. Implement domain layer - Exceptions
  - [ ] 5.1 Create domain exception classes
    - EventNotFoundException
    - VenueNotFoundException
    - InvalidEventStateException
    - CapacityExceededException
    - InvalidDateException
    - InvalidPriceException
    - PublishingException
    - _Requirements: 1.4, 1.5, 1.6, 1.7, 2.4, 4.2, 5.3, 13.1, 13.2_

- [ ] 6. Implement domain layer - Ports
  - [ ] 6.1 Define repository port interfaces
    - Create EventRepository interface with save, findById, findByStatus, findPublishedEvents, delete methods
    - Create VenueRepository interface with save, findById, findAll, existsById methods
    - _Requirements: 9.1, 9.2, 10.3, 10.4_

  - [ ] 6.2 Define event publisher port interface
    - Create EventPublisher interface with publish(DomainEvent) method
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 10.3_

- [ ] 7. Checkpoint - Domain layer complete
  - Verify all domain classes compile without framework dependencies
  - Ensure all invariants are enforced in domain model
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement application layer - DTOs
  - [ ] 8.1 Create command DTOs
    - CreateEventCommand record
    - PublishEventCommand record
    - UpdateEventCommand record
    - CancelEventCommand record
    - CreateVenueCommand record
    - _Requirements: 1.1, 2.1, 6.1, 7.1, 8.1, 10.5_

  - [ ] 8.2 Create query DTOs
    - ListEventsQuery record with optional filters (type, date range)
    - GetEventDetailsQuery record
    - CheckAvailabilityQuery record
    - GetVenueDetailsQuery record
    - EventDetails record (combines Event and Venue)
    - AvailabilityInfo record
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.3, 5.1, 5.2, 8.4, 10.5_

- [ ] 9. Implement application layer - Use Case interfaces
  - [ ] 9.1 Define use case interfaces
    - CreateEventUseCase, PublishEventUseCase, UpdateEventUseCase, CancelEventUseCase
    - ListEventsUseCase, GetEventDetailsUseCase, CheckAvailabilityUseCase
    - CreateVenueUseCase, ListVenuesUseCase, GetVenueDetailsUseCase
    - _Requirements: 10.5_

- [ ] 10. Implement application layer - Use Case implementations
  - [ ] 10.1 Implement CreateEventService
    - Validate venue exists using VenueRepository
    - Validate capacity within venue limits
    - Create Event using domain factory method
    - Save Event using EventRepository
    - Return created Event with HTTP 201 semantics
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.8_

  - [ ]* 10.2 Write unit tests for CreateEventService
    - Test successful creation
    - Test venue not found error
    - Test capacity exceeds venue maximum error
    - _Requirements: 1.4, 1.6_

  - [ ] 10.3 Implement PublishEventService with transaction management
    - Load Event by id
    - Call Event.publish() domain method
    - Save updated Event
    - Publish EventCreated domain event via EventPublisher
    - Rollback transaction if EventBridge publishing fails
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 11.1_

  - [ ]* 10.4 Write property test for PublishEventService
    - **Property 4: Event Publishing Triggers Domain Event**
    - **Property 9: Invalid State Transition Rejection**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 11.1, 11.4, 11.5**

  - [ ] 10.5 Implement UpdateEventService
    - Load Event by id
    - Call Event.updateDetails() with status-aware restrictions
    - Save updated Event
    - Publish EventUpdated domain event if status is PUBLISHED
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 11.2_

  - [ ]* 10.6 Write property tests for UpdateEventService
    - **Property 17: DRAFT Event Update Permissions**
    - **Property 19: PUBLISHED Event Update Restrictions**
    - **Property 21: CANCELLED Event Update Rejection**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

  - [ ] 10.7 Implement CancelEventService
    - Load Event by id
    - Call Event.cancel() domain method
    - Save updated Event
    - Publish EventCancelled domain event
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 11.3_

  - [ ]* 10.8 Write property tests for CancelEventService
    - **Property 13: Event Cancellation Triggers Domain Event**
    - **Property 22: Already Cancelled Rejection**
    - **Property 23: Cancellation Preserves Data**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 11.3**

  - [ ] 10.9 Implement ListEventsService
    - Query EventRepository with filters (status, type, date range)
    - Return only PUBLISHED events by default
    - Apply ordering by event date ascending
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 10.10 Write property tests for ListEventsService
    - **Property 10: Published Events Filtering**
    - **Property 12: Event Type Filtering**
    - **Property 14: Date Range Filtering**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

  - [ ] 10.11 Implement GetEventDetailsService
    - Load Event by id
    - Load associated Venue by venueId
    - Combine into EventDetails DTO
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 10.12 Write property test for GetEventDetailsService
    - **Property 15: Event Details Include Venue Information**
    - **Validates: Requirements 4.1, 4.3**

  - [ ] 10.13 Implement CheckAvailabilityService
    - Load Event by id
    - Return AvailabilityInfo with total and available capacity
    - Include soldOut flag when available capacity is zero
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 10.14 Write property test for CheckAvailabilityService
    - **Property 16: Availability Response Structure**
    - **Validates: Requirements 5.1, 5.2**

  - [ ] 10.15 Implement CreateVenueService
    - Create Venue using constructor with validation
    - Save Venue using VenueRepository
    - _Requirements: 8.1, 8.2_

  - [ ]* 10.16 Write property test for CreateVenueService
    - **Property 24: Venue Creation Completeness**
    - **Validates: Requirements 8.1**

  - [ ] 10.17 Implement ListVenuesService
    - Query VenueRepository.findAll()
    - Return venues ordered by name
    - _Requirements: 8.3_

  - [ ]* 10.18 Write property test for ListVenuesService
    - **Property 26: Venue Listing Order**
    - **Validates: Requirements 8.3**

  - [ ] 10.19 Implement GetVenueDetailsService
    - Load Venue by id
    - Return Venue details
    - _Requirements: 8.4, 8.5_

  - [ ]* 10.20 Write property test for resource not found handling
    - **Property 18: Resource Not Found Handling**
    - **Validates: Requirements 4.2, 5.3, 8.5, 13.2**

- [ ] 11. Checkpoint - Application layer complete
  - Verify all use cases are implemented
  - Verify transaction boundaries are correct
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement infrastructure layer - Database entities and mappers
  - [ ] 12.1 Create JPA entities
    - Create EventEntity with all fields, constraints, and indexes
    - Create VenueEntity with all fields, constraints, and indexes
    - Add @PrePersist and @PreUpdate for timestamp management
    - _Requirements: 9.1, 9.2, 9.5_

  - [ ] 12.2 Create JPA repository interfaces
    - Create JpaEventRepository extending JpaRepository with custom query methods
    - Create JpaVenueRepository extending JpaRepository
    - _Requirements: 9.1, 9.2_

  - [ ] 12.3 Create persistence mappers
    - EventPersistenceMapper to convert between Event and EventEntity
    - VenuePersistenceMapper to convert between Venue and VenueEntity
    - _Requirements: 9.1, 9.2, 10.4_

- [ ] 13. Implement infrastructure layer - Repository adapters
  - [ ] 13.1 Implement PostgresEventRepositoryAdapter
    - Implement all EventRepository port methods
    - Use JpaEventRepository and EventPersistenceMapper
    - Add @Transactional annotations
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 10.4_

  - [ ] 13.2 Implement PostgresVenueRepositoryAdapter
    - Implement all VenueRepository port methods
    - Use JpaVenueRepository and VenuePersistenceMapper
    - Add @Transactional annotations
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 10.4_

  - [ ]* 13.3 Write property test for persistence round trip
    - **Property 20: Persistence Round Trip**
    - **Validates: Requirements 9.1, 9.2**

  - [ ]* 13.4 Write integration tests for repository adapters with Testcontainers
    - Test save and retrieve operations
    - Test query methods (findByStatus, findPublishedEvents)
    - Test transaction rollback scenarios
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 14. Implement infrastructure layer - EventBridge adapter
  - [ ] 14.1 Implement EventBridgePublisherAdapter
    - Implement EventPublisher port
    - Use AWS EventBridge SDK to publish events
    - Add @Retryable with 3 attempts and exponential backoff
    - Serialize domain events to JSON
    - Include event source as "event-service"
    - Publish to "event-management-bus"
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 10.4_

  - [ ]* 14.2 Write unit tests for EventBridgePublisherAdapter
    - Test successful publishing
    - Test retry on failure
    - Test error propagation after max retries
    - _Requirements: 11.6_

- [ ] 15. Implement infrastructure layer - REST DTOs and mappers
  - [ ] 15.1 Create REST request DTOs
    - CreateEventRequest with validation annotations
    - UpdateEventRequest with validation annotations
    - CreateVenueRequest with validation annotations
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

  - [ ] 15.2 Create REST response DTOs
    - EventResponse record
    - EventDetailsResponse record
    - AvailabilityResponse record
    - VenueResponse record
    - ErrorResponse record with correlationId
    - _Requirements: 1.8, 4.1, 5.2, 5.4, 13.5, 13.6_

  - [ ] 15.3 Create REST mappers
    - EventRestMapper to convert between domain and REST DTOs
    - VenueRestMapper to convert between domain and REST DTOs
    - _Requirements: 10.7_

- [ ] 16. Implement infrastructure layer - REST controllers
  - [ ] 16.1 Implement EventController
    - POST /api/v1/events - create event (returns 201)
    - POST /api/v1/events/{id}/publish - publish event
    - GET /api/v1/events - list events with optional filters
    - GET /api/v1/events/{id} - get event details
    - GET /api/v1/events/{id}/availability - check availability
    - PUT /api/v1/events/{id} - update event
    - DELETE /api/v1/events/{id} - cancel event
    - Use @Valid for request validation
    - _Requirements: 1.8, 2.1, 3.1, 3.2, 3.3, 4.1, 5.1, 6.1, 7.1, 10.7, 12.6_

  - [ ] 16.2 Implement VenueController
    - POST /api/v1/venues - create venue (returns 201)
    - GET /api/v1/venues - list venues
    - GET /api/v1/venues/{id} - get venue details
    - Use @Valid for request validation
    - _Requirements: 8.1, 8.3, 8.4, 10.7, 12.6_

  - [ ]* 16.3 Write property tests for input validation
    - **Property 28: Event Name Validation**
    - **Property 29: Event Description Validation**
    - **Property 30: Event Type Validation**
    - **Property 31: Venue Name Validation**
    - **Property 32: Venue Location Validation**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6**

  - [ ]* 16.4 Write integration tests for REST controllers
    - Test successful requests return correct status codes
    - Test validation errors return 400
    - Test resource not found returns 404
    - _Requirements: 1.8, 12.6, 13.1, 13.2_

- [ ] 17. Implement infrastructure layer - Global exception handler
  - [ ] 17.1 Create GlobalExceptionHandler
    - Handle ValidationException → 400 with VALIDATION_ERROR code
    - Handle domain exceptions → 400 with specific error codes
    - Handle NotFoundException → 404
    - Handle infrastructure exceptions → 500
    - Generate correlation ID for all errors
    - Log errors with appropriate levels (WARN for client errors, ERROR for server errors)
    - Never expose stack traces or internal details in responses
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [ ]* 17.2 Write property tests for error handling
    - **Property 33: Domain Rule Violation Response**
    - **Property 34: Error Response Correlation**
    - **Property 35: Error Response Security**
    - **Property 36: Successful Creation HTTP Status**
    - **Validates: Requirements 1.8, 13.1, 13.2, 13.5, 13.6**

- [ ] 18. Implement infrastructure layer - Configuration
  - [ ] 18.1 Create Spring configuration classes
    - ApplicationConfig - wire use cases with adapters
    - DatabaseConfig - JPA and Flyway configuration
    - AwsConfig - EventBridge client bean
    - LocalStackConfig - LocalStack-specific configuration for local profile
    - _Requirements: 10.1, 10.4, 14.1, 14.2, 14.3, 14.4_

  - [ ] 18.2 Create application.yml files
    - application.yml - base configuration
    - application-local.yml - LocalStack endpoints and credentials
    - Configure datasource, JPA, Flyway, AWS region, EventBridge bus name
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [ ] 19. Create database migrations
  - [ ] 19.1 Create Flyway migration scripts
    - V1__create_venues_table.sql with constraints and indexes
    - V2__create_events_table.sql with constraints, foreign keys, and indexes
    - _Requirements: 9.1, 9.2, 9.5, 14.5_

- [ ] 20. Checkpoint - Infrastructure layer complete
  - Verify all adapters are wired correctly
  - Verify configuration loads for local profile
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 21. Create project build and deployment files
  - [ ] 21.1 Configure Maven pom.xml
    - Set Java 17+ and Spring Boot 3.x
    - Add all runtime dependencies (Spring Boot starters, PostgreSQL, AWS SDK)
    - Add all test dependencies (JUnit 5, Mockito, AssertJ, jqwik, Testcontainers)
    - Configure Maven plugins (Spring Boot, Surefire, Jacoco for coverage)
    - _Requirements: 10.1_

  - [ ] 21.2 Create Dockerfile
    - Multi-stage build with Maven
    - Use Java 17+ base image
    - Expose port 8080
    - _Requirements: 14.1_

  - [ ] 21.3 Create README.md
    - Document project structure
    - Document how to run locally with LocalStack
    - Document API endpoints with examples
    - Document testing approach
    - _Requirements: 14.1, 14.2_

- [ ] 22. End-to-end integration testing
  - [ ]* 22.1 Write integration test with Testcontainers and LocalStack
    - Start PostgreSQL and LocalStack containers
    - Create venue via REST API
    - Create event via REST API
    - Publish event and verify EventCreated published to EventBridge
    - Update event and verify EventUpdated published
    - Cancel event and verify EventCancelled published
    - List events and verify filtering
    - Verify all data persisted correctly
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 6.1, 7.1, 8.1, 9.1, 11.1, 14.1, 14.2_

- [ ] 23. Final checkpoint - Complete system validation
  - Run all tests (unit, property-based, integration)
  - Verify test coverage meets goals (domain 100%, application 95%+, infrastructure 80%+)
  - Start service locally with LocalStack
  - Manually test all API endpoints
  - Verify EventBridge events are published correctly
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate the complete system with real infrastructure
- Checkpoints ensure incremental validation at layer boundaries
- Implementation follows bottom-up approach: domain → application → infrastructure
- All domain logic is framework-independent and highly testable
