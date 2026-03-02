# Event Service - Design Document

## Overview

The Event Service is the foundational microservice in the event management platform, responsible for managing the complete lifecycle of events (concerts, conferences, sports) and their associated venues. This service implements Hexagonal Architecture (Ports & Adapters) to maintain a clean separation between business logic and infrastructure concerns.

### Core Responsibilities

- Event lifecycle management (create, publish, update, cancel)
- Venue management (create, list, retrieve)
- Event availability tracking
- Domain event publishing to EventBridge for inter-service communication
- Data persistence using PostgreSQL

### Architectural Pattern

The service follows Hexagonal Architecture with three distinct layers:

- **Domain Layer**: Pure business logic with aggregates, value objects, and port interfaces
- **Application Layer**: Use case orchestration and transaction boundaries
- **Infrastructure Layer**: Adapters implementing ports (PostgreSQL, EventBridge, REST API)

This architecture ensures the domain logic remains independent of frameworks, databases, and external services, making it highly testable and maintainable.

### Technology Stack

- **Language**: Java 17+
- **Framework**: Spring Boot 3.x
- **Database**: PostgreSQL (via LocalStack RDS)
- **Messaging**: AWS EventBridge (via LocalStack)
- **Build Tool**: Maven
- **Testing**: JUnit 5, Mockito, Testcontainers

## Architecture

### Hexagonal Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ REST         │  │ PostgreSQL   │  │ EventBridge  │      │
│  │ Controller   │  │ Adapter      │  │ Adapter      │      │
│  │ (IN)         │  │ (OUT)        │  │ (OUT)        │      │
│  └──────┬───────┘  └──────▲───────┘  └──────▲───────┘      │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
┌─────────▼─────────────────┼──────────────────┼──────────────┐
│         │    Application Layer                │              │
│  ┌──────▼───────┐  ┌─────────────┐  ┌────────▼────────┐    │
│  │ Use Cases    │  │ Use Cases   │  │ Use Cases       │    │
│  │ (Create,     │  │ (List,      │  │ (Publish,       │    │
│  │  Update)     │  │  Get)       │  │  Cancel)        │    │
│  └──────┬───────┘  └─────┬───────┘  └────────┬────────┘    │
│         │                │                    │              │
└─────────┼────────────────┼────────────────────┼──────────────┘
          │                │                    │
┌─────────▼────────────────▼────────────────────▼──────────────┐
│                       Domain Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Event        │  │ Venue        │  │ Ports        │       │
│  │ Aggregate    │  │ Aggregate    │  │ (Interfaces) │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ Value        │  │ Domain       │                         │
│  │ Objects      │  │ Services     │                         │
│  └──────────────┘  └──────────────┘                         │
└───────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**Domain Layer** (Core Business Logic):
- Defines Event and Venue aggregates with business rules
- Enforces invariants (capacity limits, status transitions, date validation)
- Declares port interfaces (EventRepository, VenueRepository, EventPublisher)
- Contains value objects (EventDate, Capacity, Price, Location, EventStatus)
- No dependencies on frameworks or infrastructure

**Application Layer** (Use Case Orchestration):
- Implements use cases that coordinate domain operations
- Manages transaction boundaries
- Translates between domain and infrastructure concerns
- Handles cross-cutting concerns (logging, validation)

**Infrastructure Layer** (Technical Implementation):
- REST controllers (IN adapter) - HTTP request/response handling
- PostgreSQL adapter (OUT adapter) - Data persistence
- EventBridge adapter (OUT adapter) - Event publishing
- Configuration and framework integration

### Event Flow Example

```
User Request → REST Controller → Use Case → Domain Service → Repository Port
                                                           ↓
                                                    PostgreSQL Adapter
                                                           ↓
                                                      Database
```

## Components and Interfaces

### Domain Model

#### Event Aggregate

The Event aggregate is the core entity representing an event with its complete lifecycle.

```java
public class Event {
    private EventId id;
    private String name;
    private String description;
    private EventType type;
    private VenueId venueId;
    private EventDate eventDate;
    private Capacity totalCapacity;
    private Capacity availableCapacity;
    private Price price;
    private EventStatus status;
    private Instant createdAt;
    private Instant updatedAt;
    
    // Business methods
    public void publish();
    public void cancel();
    public void updateDetails(String name, String description, Price price);
    public boolean canBePublished();
    public boolean canBeCancelled();
    public boolean canBeUpdated();
}
```

**Invariants**:
- Available capacity cannot exceed total capacity
- Total capacity cannot exceed venue maximum capacity
- Event date must be in the future at creation time
- Price must be non-negative
- Status transitions follow: DRAFT → PUBLISHED → CANCELLED
- Only DRAFT events can have all fields modified
- PUBLISHED events can only modify description and price
- CANCELLED events cannot be modified

#### Venue Aggregate

```java
public class Venue {
    private VenueId id;
    private String name;
    private Location location;
    private Capacity maxCapacity;
    private Instant createdAt;
    private Instant updatedAt;
    
    // Business methods
    public boolean canAccommodate(Capacity eventCapacity);
}
```

**Invariants**:
- Maximum capacity must be positive
- Name cannot be empty
- Location must be complete (address, city, country)

#### Value Objects

```java
public record EventId(UUID value) {}
public record VenueId(UUID value) {}
public record EventDate(LocalDateTime value) {
    public boolean isInFuture() { ... }
}
public record Capacity(int value) {
    public Capacity {
        if (value < 0) throw new IllegalArgumentException();
    }
    public boolean isAvailable() { return value > 0; }
}
public record Price(BigDecimal amount, String currency) {
    public Price {
        if (amount.compareTo(BigDecimal.ZERO) < 0) 
            throw new IllegalArgumentException();
    }
}
public record Location(String address, String city, String country) {}
public enum EventType { CONCERT, CONFERENCE, SPORTS }
public enum EventStatus { DRAFT, PUBLISHED, CANCELLED }
```

#### Domain Events

```java
public sealed interface DomainEvent permits EventCreated, EventUpdated, EventCancelled {
    EventId eventId();
    Instant occurredAt();
}

public record EventCreated(
    EventId eventId,
    String name,
    VenueId venueId,
    EventDate eventDate,
    Capacity availableCapacity,
    Price price,
    Instant occurredAt
) implements DomainEvent {}

public record EventUpdated(
    EventId eventId,
    Map<String, Object> updatedFields,
    Instant occurredAt
) implements DomainEvent {}

public record EventCancelled(
    EventId eventId,
    Instant occurredAt
) implements DomainEvent {}
```

### Ports (Interfaces)

#### Output Ports

```java
public interface EventRepository {
    Event save(Event event);
    Optional<Event> findById(EventId id);
    List<Event> findByStatus(EventStatus status);
    List<Event> findByTypeAndDateRange(EventType type, LocalDateTime start, LocalDateTime end);
    List<Event> findPublishedEvents(EventType type, LocalDateTime start, LocalDateTime end);
    void delete(EventId id);
}

public interface VenueRepository {
    Venue save(Venue venue);
    Optional<Venue> findById(VenueId id);
    List<Venue> findAll();
    boolean existsById(VenueId id);
}

public interface EventPublisher {
    void publish(DomainEvent event) throws PublishingException;
}
```

#### Input Ports (Use Cases)

```java
public interface CreateEventUseCase {
    Event execute(CreateEventCommand command);
}

public interface PublishEventUseCase {
    Event execute(PublishEventCommand command);
}

public interface ListEventsUseCase {
    List<Event> execute(ListEventsQuery query);
}

public interface GetEventDetailsUseCase {
    EventDetails execute(GetEventDetailsQuery query);
}

public interface CheckAvailabilityUseCase {
    AvailabilityInfo execute(CheckAvailabilityQuery query);
}

public interface UpdateEventUseCase {
    Event execute(UpdateEventCommand command);
}

public interface CancelEventUseCase {
    Event execute(CancelEventCommand command);
}

public interface CreateVenueUseCase {
    Venue execute(CreateVenueCommand command);
}

public interface ListVenuesUseCase {
    List<Venue> execute();
}

public interface GetVenueDetailsUseCase {
    Venue execute(GetVenueDetailsQuery query);
}
```

### Adapters

#### REST Controller (IN Adapter)

```java
@RestController
@RequestMapping("/api/v1/events")
public class EventController {
    
    @PostMapping
    public ResponseEntity<EventResponse> createEvent(@Valid @RequestBody CreateEventRequest request);
    
    @PostMapping("/{id}/publish")
    public ResponseEntity<EventResponse> publishEvent(@PathVariable UUID id);
    
    @GetMapping
    public ResponseEntity<List<EventResponse>> listEvents(
        @RequestParam(required = false) EventType type,
        @RequestParam(required = false) LocalDateTime startDate,
        @RequestParam(required = false) LocalDateTime endDate
    );
    
    @GetMapping("/{id}")
    public ResponseEntity<EventDetailsResponse> getEventDetails(@PathVariable UUID id);
    
    @GetMapping("/{id}/availability")
    public ResponseEntity<AvailabilityResponse> checkAvailability(@PathVariable UUID id);
    
    @PutMapping("/{id}")
    public ResponseEntity<EventResponse> updateEvent(
        @PathVariable UUID id,
        @Valid @RequestBody UpdateEventRequest request
    );
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> cancelEvent(@PathVariable UUID id);
}

@RestController
@RequestMapping("/api/v1/venues")
public class VenueController {
    
    @PostMapping
    public ResponseEntity<VenueResponse> createVenue(@Valid @RequestBody CreateVenueRequest request);
    
    @GetMapping
    public ResponseEntity<List<VenueResponse>> listVenues();
    
    @GetMapping("/{id}")
    public ResponseEntity<VenueResponse> getVenueDetails(@PathVariable UUID id);
}
```

#### PostgreSQL Adapter (OUT Adapter)

```java
@Repository
public class PostgresEventRepositoryAdapter implements EventRepository {
    
    private final JpaEventRepository jpaRepository;
    private final EventMapper mapper;
    
    @Override
    @Transactional
    public Event save(Event event) {
        EventEntity entity = mapper.toEntity(event);
        EventEntity saved = jpaRepository.save(entity);
        return mapper.toDomain(saved);
    }
    
    @Override
    @Transactional(readOnly = true)
    public Optional<Event> findById(EventId id) {
        return jpaRepository.findById(id.value())
            .map(mapper::toDomain);
    }
    
    // Additional methods...
}

@Repository
public class PostgresVenueRepositoryAdapter implements VenueRepository {
    
    private final JpaVenueRepository jpaRepository;
    private final VenueMapper mapper;
    
    // Implementation...
}
```

#### EventBridge Adapter (OUT Adapter)

```java
@Component
public class EventBridgePublisherAdapter implements EventPublisher {
    
    private final EventBridgeClient eventBridgeClient;
    private final String eventBusName = "event-management-bus";
    private final String eventSource = "event-service";
    
    @Override
    @Retryable(maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public void publish(DomainEvent event) throws PublishingException {
        try {
            PutEventsRequestEntry entry = PutEventsRequestEntry.builder()
                .eventBusName(eventBusName)
                .source(eventSource)
                .detailType(event.getClass().getSimpleName())
                .detail(serializeEvent(event))
                .build();
            
            PutEventsRequest request = PutEventsRequest.builder()
                .entries(entry)
                .build();
            
            PutEventsResponse response = eventBridgeClient.putEvents(request);
            
            if (response.failedEntryCount() > 0) {
                throw new PublishingException("Failed to publish event");
            }
        } catch (Exception e) {
            throw new PublishingException("EventBridge publishing failed", e);
        }
    }
    
    private String serializeEvent(DomainEvent event) {
        // JSON serialization
    }
}
```

### Application Services (Use Case Implementations)

```java
@Service
@Transactional
public class CreateEventService implements CreateEventUseCase {
    
    private final EventRepository eventRepository;
    private final VenueRepository venueRepository;
    
    @Override
    public Event execute(CreateEventCommand command) {
        // Validate venue exists
        Venue venue = venueRepository.findById(command.venueId())
            .orElseThrow(() -> new VenueNotFoundException(command.venueId()));
        
        // Validate capacity
        if (!venue.canAccommodate(command.totalCapacity())) {
            throw new CapacityExceededException();
        }
        
        // Create event
        Event event = Event.create(
            command.name(),
            command.description(),
            command.type(),
            command.venueId(),
            command.eventDate(),
            command.totalCapacity(),
            command.price()
        );
        
        return eventRepository.save(event);
    }
}

@Service
@Transactional
public class PublishEventService implements PublishEventUseCase {
    
    private final EventRepository eventRepository;
    private final EventPublisher eventPublisher;
    
    @Override
    public Event execute(PublishEventCommand command) {
        Event event = eventRepository.findById(command.eventId())
            .orElseThrow(() -> new EventNotFoundException(command.eventId()));
        
        // Domain logic handles status transition validation
        event.publish();
        
        Event savedEvent = eventRepository.save(event);
        
        // Publish domain event
        try {
            EventCreated domainEvent = new EventCreated(
                savedEvent.getId(),
                savedEvent.getName(),
                savedEvent.getVenueId(),
                savedEvent.getEventDate(),
                savedEvent.getAvailableCapacity(),
                savedEvent.getPrice(),
                Instant.now()
            );
            eventPublisher.publish(domainEvent);
        } catch (PublishingException e) {
            // Rollback handled by @Transactional
            throw new EventPublishingFailedException(e);
        }
        
        return savedEvent;
    }
}
```

## Data Models

### Database Schema

#### Events Table

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    venue_id UUID NOT NULL,
    event_date TIMESTAMP NOT NULL,
    total_capacity INTEGER NOT NULL,
    available_capacity INTEGER NOT NULL,
    price_amount DECIMAL(10, 2) NOT NULL,
    price_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_venue FOREIGN KEY (venue_id) REFERENCES venues(id),
    CONSTRAINT chk_capacity CHECK (available_capacity >= 0 AND available_capacity <= total_capacity),
    CONSTRAINT chk_price CHECK (price_amount >= 0),
    CONSTRAINT chk_status CHECK (status IN ('DRAFT', 'PUBLISHED', 'CANCELLED'))
);

CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_venue ON events(venue_id);
```

#### Venues Table

```sql
CREATE TABLE venues (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    max_capacity INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_max_capacity CHECK (max_capacity > 0)
);

CREATE INDEX idx_venues_name ON venues(name);
CREATE INDEX idx_venues_city ON venues(city);
```

### JPA Entities

```java
@Entity
@Table(name = "events")
public class EventEntity {
    @Id
    private UUID id;
    
    @Column(nullable = false, length = 200)
    private String name;
    
    @Column(length = 2000)
    private String description;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "event_type", nullable = false)
    private EventType type;
    
    @Column(name = "venue_id", nullable = false)
    private UUID venueId;
    
    @Column(name = "event_date", nullable = false)
    private LocalDateTime eventDate;
    
    @Column(name = "total_capacity", nullable = false)
    private Integer totalCapacity;
    
    @Column(name = "available_capacity", nullable = false)
    private Integer availableCapacity;
    
    @Column(name = "price_amount", nullable = false)
    private BigDecimal priceAmount;
    
    @Column(name = "price_currency", nullable = false, length = 3)
    private String priceCurrency;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EventStatus status;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;
    
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = Instant.now();
        updatedAt = Instant.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = Instant.now();
    }
}

@Entity
@Table(name = "venues")
public class VenueEntity {
    @Id
    private UUID id;
    
    @Column(nullable = false, length = 200)
    private String name;
    
    @Column(nullable = false, length = 500)
    private String address;
    
    @Column(nullable = false, length = 100)
    private String city;
    
    @Column(nullable = false, length = 100)
    private String country;
    
    @Column(name = "max_capacity", nullable = false)
    private Integer maxCapacity;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;
    
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = Instant.now();
        updatedAt = Instant.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = Instant.now();
    }
}
```

### EventBridge Event Schema

```json
{
  "version": "1.0",
  "source": "event-service",
  "detail-type": "EventCreated",
  "detail": {
    "eventId": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Summer Music Festival",
    "venueId": "660e8400-e29b-41d4-a716-446655440000",
    "eventDate": "2024-07-15T18:00:00Z",
    "availableCapacity": 5000,
    "price": {
      "amount": 75.00,
      "currency": "USD"
    },
    "occurredAt": "2024-01-15T10:30:00Z"
  }
}
```

## Project Structure

```
event-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── eventmanagement/
│   │   │           └── eventservice/
│   │   │               ├── domain/                    # Domain Layer
│   │   │               │   ├── model/
│   │   │               │   │   ├── Event.java
│   │   │               │   │   ├── Venue.java
│   │   │               │   │   ├── EventId.java
│   │   │               │   │   ├── VenueId.java
│   │   │               │   │   ├── EventDate.java
│   │   │               │   │   ├── Capacity.java
│   │   │               │   │   ├── Price.java
│   │   │               │   │   ├── Location.java
│   │   │               │   │   ├── EventType.java
│   │   │               │   │   └── EventStatus.java
│   │   │               │   ├── event/
│   │   │               │   │   ├── DomainEvent.java
│   │   │               │   │   ├── EventCreated.java
│   │   │               │   │   ├── EventUpdated.java
│   │   │               │   │   └── EventCancelled.java
│   │   │               │   ├── exception/
│   │   │               │   │   ├── EventNotFoundException.java
│   │   │               │   │   ├── VenueNotFoundException.java
│   │   │               │   │   ├── InvalidEventStateException.java
│   │   │               │   │   ├── CapacityExceededException.java
│   │   │               │   │   └── PublishingException.java
│   │   │               │   └── port/
│   │   │               │       ├── EventRepository.java
│   │   │               │       ├── VenueRepository.java
│   │   │               │       └── EventPublisher.java
│   │   │               ├── application/               # Application Layer
│   │   │               │   ├── usecase/
│   │   │               │   │   ├── CreateEventUseCase.java
│   │   │               │   │   ├── PublishEventUseCase.java
│   │   │               │   │   ├── ListEventsUseCase.java
│   │   │               │   │   ├── GetEventDetailsUseCase.java
│   │   │               │   │   ├── CheckAvailabilityUseCase.java
│   │   │               │   │   ├── UpdateEventUseCase.java
│   │   │               │   │   ├── CancelEventUseCase.java
│   │   │               │   │   ├── CreateVenueUseCase.java
│   │   │               │   │   ├── ListVenuesUseCase.java
│   │   │               │   │   └── GetVenueDetailsUseCase.java
│   │   │               │   ├── service/
│   │   │               │   │   ├── CreateEventService.java
│   │   │               │   │   ├── PublishEventService.java
│   │   │               │   │   ├── ListEventsService.java
│   │   │               │   │   ├── GetEventDetailsService.java
│   │   │               │   │   ├── CheckAvailabilityService.java
│   │   │               │   │   ├── UpdateEventService.java
│   │   │               │   │   ├── CancelEventService.java
│   │   │               │   │   ├── CreateVenueService.java
│   │   │               │   │   ├── ListVenuesService.java
│   │   │               │   │   └── GetVenueDetailsService.java
│   │   │               │   └── dto/
│   │   │               │       ├── command/
│   │   │               │       │   ├── CreateEventCommand.java
│   │   │               │       │   ├── PublishEventCommand.java
│   │   │               │       │   ├── UpdateEventCommand.java
│   │   │               │       │   ├── CancelEventCommand.java
│   │   │               │       │   └── CreateVenueCommand.java
│   │   │               │       └── query/
│   │   │               │           ├── ListEventsQuery.java
│   │   │               │           ├── GetEventDetailsQuery.java
│   │   │               │           ├── CheckAvailabilityQuery.java
│   │   │               │           └── GetVenueDetailsQuery.java
│   │   │               └── infrastructure/           # Infrastructure Layer
│   │   │                   ├── adapter/
│   │   │                   │   ├── in/
│   │   │                   │   │   └── rest/
│   │   │                   │   │       ├── EventController.java
│   │   │                   │   │       ├── VenueController.java
│   │   │                   │   │       ├── dto/
│   │   │                   │   │       │   ├── CreateEventRequest.java
│   │   │                   │   │       │   ├── UpdateEventRequest.java
│   │   │                   │   │       │   ├── EventResponse.java
│   │   │                   │   │       │   ├── EventDetailsResponse.java
│   │   │                   │   │       │   ├── AvailabilityResponse.java
│   │   │                   │   │       │   ├── CreateVenueRequest.java
│   │   │                   │   │       │   └── VenueResponse.java
│   │   │                   │   │       └── mapper/
│   │   │                   │   │           ├── EventRestMapper.java
│   │   │                   │   │           └── VenueRestMapper.java
│   │   │                   │   └── out/
│   │   │                   │       ├── persistence/
│   │   │                   │       │   ├── PostgresEventRepositoryAdapter.java
│   │   │                   │       │   ├── PostgresVenueRepositoryAdapter.java
│   │   │                   │       │   ├── entity/
│   │   │                   │       │   │   ├── EventEntity.java
│   │   │                   │       │   │   └── VenueEntity.java
│   │   │                   │       │   ├── jpa/
│   │   │                   │       │   │   ├── JpaEventRepository.java
│   │   │                   │       │   │   └── JpaVenueRepository.java
│   │   │                   │       │   └── mapper/
│   │   │                   │       │       ├── EventPersistenceMapper.java
│   │   │                   │       │       └── VenuePersistenceMapper.java
│   │   │                   │       └── messaging/
│   │   │                   │           ├── EventBridgePublisherAdapter.java
│   │   │                   │           └── EventBridgeConfig.java
│   │   │                   ├── config/
│   │   │                   │   ├── ApplicationConfig.java
│   │   │                   │   ├── DatabaseConfig.java
│   │   │                   │   ├── AwsConfig.java
│   │   │                   │   └── LocalStackConfig.java
│   │   │                   └── exception/
│   │   │                       ├── GlobalExceptionHandler.java
│   │   │                       └── ErrorResponse.java
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-local.yml
│   │       ├── application-dev.yml
│   │       ├── application-prod.yml
│   │       └── db/
│   │           └── migration/
│   │               ├── V1__create_venues_table.sql
│   │               └── V2__create_events_table.sql
│   └── test/
│       └── java/
│           └── com/
│               └── eventmanagement/
│                   └── eventservice/
│                       ├── domain/
│                       │   └── model/
│                       │       ├── EventTest.java
│                       │       └── VenueTest.java
│                       ├── application/
│                       │   └── service/
│                       │       ├── CreateEventServiceTest.java
│                       │       ├── PublishEventServiceTest.java
│                       │       └── ...
│                       └── infrastructure/
│                           ├── adapter/
│                           │   ├── rest/
│                           │   │   ├── EventControllerTest.java
│                           │   │   └── VenueControllerTest.java
│                           │   └── persistence/
│                           │       ├── PostgresEventRepositoryAdapterTest.java
│                           │       └── PostgresVenueRepositoryAdapterTest.java
│                           └── integration/
│                               ├── EventServiceIntegrationTest.java
│                               └── VenueServiceIntegrationTest.java
├── pom.xml
├── Dockerfile
└── README.md
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, I identified several areas of redundancy:

- Requirements 2.2, 2.3, 11.1 all describe EventCreated publishing → Combined into Property 4
- Requirements 6.5, 11.2 both describe EventUpdated publishing → Combined into Property 11
- Requirements 7.2, 7.3, 11.3 all describe EventCancelled publishing → Combined into Property 13
- Requirements 4.2, 5.3, 8.5, 13.2 all test 404 responses → Combined into Property 18
- Requirements 9.1 and 9.2 both test persistence round-trip → Combined into Property 20
- Multiple validation requirements (12.1-12.6, 13.1) test error responses → Grouped into Properties 23-26

### Property 1: Event Creation Completeness

For any valid event creation request (with valid venue, future date, capacity within venue limits, non-negative price), the created Event should contain all required fields: unique identifier, name, description, event type, venue reference, event date, total capacity, available capacity, and price.

**Validates: Requirements 1.1**

### Property 2: New Events Start in DRAFT Status

For any newly created Event, the Event_Status should be DRAFT.

**Validates: Requirements 1.2**

### Property 3: Initial Capacity Invariant

For any newly created Event, the Available_Capacity should equal the total capacity.

**Validates: Requirements 1.3**

### Property 4: Event Publishing Triggers Domain Event

For any Event in DRAFT status, when published, the system should transition the Event_Status to PUBLISHED and publish an EventCreated domain event containing event identifier, name, venue identifier, event date, available capacity, and price to the "event-management-bus" with source "event-service".

**Validates: Requirements 2.1, 2.2, 2.3, 11.1, 11.4, 11.5**

### Property 5: Invalid Venue Reference Rejection

For any event creation request with a non-existent venue identifier, the system should return an error indicating invalid venue.

**Validates: Requirements 1.4**

### Property 6: Past Date Rejection

For any event creation request with an event date in the past, the system should return an error indicating invalid date.

**Validates: Requirements 1.5**

### Property 7: Capacity Limit Enforcement

For any event creation request where total capacity exceeds the venue's maximum capacity, the system should return an error indicating capacity limit exceeded.

**Validates: Requirements 1.6**

### Property 8: Negative Price Rejection

For any event creation request with a negative price, the system should return an error indicating invalid price.

**Validates: Requirements 1.7**

### Property 9: Invalid State Transition Rejection

For any Event not in DRAFT status, a publish request should return an error indicating invalid state transition.

**Validates: Requirements 2.4**

### Property 10: Published Events Filtering

For any list events request without filters, the system should return only Events with PUBLISHED status, ordered by event date in ascending order.

**Validates: Requirements 3.1, 3.4**

### Property 11: Event Update Triggers Domain Event

For any Event in PUBLISHED status, when updated (description or price), the system should publish an EventUpdated domain event containing the event identifier and updated fields to EventBridge.

**Validates: Requirements 6.5, 11.2**

### Property 12: Event Type Filtering

For any event type filter (CONCERT, CONFERENCE, or SPORTS), the system should return only published Events matching that type, ordered by event date in ascending order.

**Validates: Requirements 3.2, 3.4**

### Property 13: Event Cancellation Triggers Domain Event

For any Event in DRAFT or PUBLISHED status, when cancelled, the system should transition the Event_Status to CANCELLED and publish an EventCancelled domain event containing event identifier and cancellation timestamp to EventBridge.

**Validates: Requirements 7.1, 7.2, 7.3, 11.3**

### Property 14: Date Range Filtering

For any date range filter (start and end dates), the system should return only published Events with event dates within that range, ordered by event date in ascending order.

**Validates: Requirements 3.3, 3.4**

### Property 15: Event Details Include Venue Information

For any valid event identifier, retrieving event details should return the Event with all details including the associated Venue information (name, location, maximum capacity).

**Validates: Requirements 4.1, 4.3**

### Property 16: Availability Response Structure

For any valid event identifier, checking availability should return both the total capacity and Available_Capacity.

**Validates: Requirements 5.1, 5.2**

### Property 17: DRAFT Event Update Permissions

For any Event in DRAFT status, update requests should successfully modify name, description, and price, but should not modify event date, venue, or total capacity.

**Validates: Requirements 6.1, 6.2**

### Property 18: Resource Not Found Handling

For any non-existent identifier (event or venue), the system should return an error with HTTP status 404.

**Validates: Requirements 4.2, 5.3, 8.5, 13.2**

### Property 19: PUBLISHED Event Update Restrictions

For any Event in PUBLISHED status, update requests should only successfully modify description and price; attempts to modify other fields should leave them unchanged.

**Validates: Requirements 6.3, 6.2**

### Property 20: Persistence Round Trip

For any Event or Venue, after saving to the database and retrieving by identifier, all attributes should be preserved (serialization/deserialization identity).

**Validates: Requirements 9.1, 9.2**

### Property 21: CANCELLED Event Update Rejection

For any Event in CANCELLED status, update requests should return an error indicating the event cannot be modified.

**Validates: Requirements 6.4**

### Property 22: Already Cancelled Rejection

For any Event already in CANCELLED status, a cancel request should return an error indicating the event is already cancelled.

**Validates: Requirements 7.4**

### Property 23: Cancellation Preserves Data

For any Event that is cancelled, all event data should remain retrievable (no deletion occurs).

**Validates: Requirements 7.5**

### Property 24: Venue Creation Completeness

For any valid venue creation request (with non-empty name, complete location, and positive maximum capacity), the created Venue should contain all required fields: unique identifier, name, location (address, city, country), and maximum capacity.

**Validates: Requirements 8.1**

### Property 25: Invalid Venue Capacity Rejection

For any venue creation request with maximum capacity less than or equal to zero, the system should return an error indicating invalid capacity.

**Validates: Requirements 8.2**

### Property 26: Venue Listing Order

For any venue list request, the system should return all Venues ordered by name in ascending order.

**Validates: Requirements 8.3**

### Property 27: Venue Retrieval

For any valid venue identifier, the system should return the complete Venue details.

**Validates: Requirements 8.4**

### Property 28: Event Name Validation

For any event creation request with an empty name or name exceeding 200 characters, the system should return an error with HTTP status 400.

**Validates: Requirements 12.1, 12.6**

### Property 29: Event Description Validation

For any event creation request with description exceeding 2000 characters, the system should return an error with HTTP status 400.

**Validates: Requirements 12.2, 12.6**

### Property 30: Event Type Validation

For any event creation request with an event type not in {CONCERT, CONFERENCE, SPORTS}, the system should return an error with HTTP status 400.

**Validates: Requirements 12.3, 12.6**

### Property 31: Venue Name Validation

For any venue creation request with an empty name or name exceeding 200 characters, the system should return an error with HTTP status 400.

**Validates: Requirements 12.4, 12.6**

### Property 32: Venue Location Validation

For any venue creation request with empty address, city, or country, the system should return an error with HTTP status 400.

**Validates: Requirements 12.5, 12.6**

### Property 33: Domain Rule Violation Response

For any domain rule violation (invalid state transition, capacity exceeded, etc.), the system should return an error response with HTTP status 400 and an error code.

**Validates: Requirements 13.1**

### Property 34: Error Response Correlation

For any error response, the system should include a correlation identifier for tracing.

**Validates: Requirements 13.5**

### Property 35: Error Response Security

For any error response, the system should not expose internal implementation details or stack traces.

**Validates: Requirements 13.6**

### Property 36: Successful Creation HTTP Status

For any successful event creation, the system should return HTTP status 201.

**Validates: Requirements 1.8**


## Error Handling

### Error Categories

The Event Service implements a comprehensive error handling strategy that categorizes errors into distinct types, each with appropriate HTTP status codes and error responses.

#### 1. Validation Errors (HTTP 400)

Validation errors occur when client input fails to meet the required format or business rules.

**Examples**:
- Empty or oversized field values (name > 200 chars, description > 2000 chars)
- Invalid enum values (event type not in {CONCERT, CONFERENCE, SPORTS})
- Missing required fields
- Malformed data types

**Response Structure**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "status": 400,
  "error": "Bad Request",
  "errorCode": "VALIDATION_ERROR",
  "message": "Event name cannot exceed 200 characters",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "path": "/api/v1/events"
}
```

#### 2. Domain Rule Violations (HTTP 400)

Domain rule violations occur when business logic constraints are not satisfied.

**Examples**:
- Event date in the past
- Capacity exceeds venue maximum
- Negative price
- Invalid state transition (publishing non-DRAFT event)
- Updating CANCELLED event

**Response Structure**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "status": 400,
  "error": "Bad Request",
  "errorCode": "CAPACITY_EXCEEDED",
  "message": "Event capacity (6000) exceeds venue maximum capacity (5000)",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "path": "/api/v1/events"
}
```

#### 3. Resource Not Found (HTTP 404)

Resource not found errors occur when a requested entity does not exist.

**Examples**:
- Event ID not found
- Venue ID not found
- Referenced venue does not exist during event creation

**Response Structure**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "status": 404,
  "error": "Not Found",
  "errorCode": "EVENT_NOT_FOUND",
  "message": "Event with ID 550e8400-e29b-41d4-a716-446655440000 not found",
  "correlationId": "660e8400-e29b-41d4-a716-446655440000",
  "path": "/api/v1/events/550e8400-e29b-41d4-a716-446655440000"
}
```

#### 4. Infrastructure Errors (HTTP 500)

Infrastructure errors occur when external systems or internal components fail.

**Examples**:
- Database connection failure
- EventBridge publishing failure after retries
- Transaction rollback due to constraint violation
- Unexpected runtime exceptions

**Response Structure**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "status": 500,
  "error": "Internal Server Error",
  "errorCode": "DATABASE_ERROR",
  "message": "An unexpected error occurred. Please try again later.",
  "correlationId": "770e8400-e29b-41d4-a716-446655440000",
  "path": "/api/v1/events"
}
```

**Note**: Internal error details (stack traces, SQL queries, connection strings) are logged but never exposed to clients.

### Error Handling Implementation

#### Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(
            ValidationException ex, HttpServletRequest request) {
        String correlationId = UUID.randomUUID().toString();
        logger.warn("Validation error [{}]: {}", correlationId, ex.getMessage());
        
        ErrorResponse error = new ErrorResponse(
            Instant.now(),
            HttpStatus.BAD_REQUEST.value(),
            "Bad Request",
            "VALIDATION_ERROR",
            ex.getMessage(),
            correlationId,
            request.getRequestURI()
        );
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }
    
    @ExceptionHandler({
        InvalidEventStateException.class,
        CapacityExceededException.class,
        InvalidDateException.class,
        InvalidPriceException.class
    })
    public ResponseEntity<ErrorResponse> handleDomainException(
            RuntimeException ex, HttpServletRequest request) {
        String correlationId = UUID.randomUUID().toString();
        logger.warn("Domain rule violation [{}]: {}", correlationId, ex.getMessage());
        
        String errorCode = determineErrorCode(ex);
        ErrorResponse error = new ErrorResponse(
            Instant.now(),
            HttpStatus.BAD_REQUEST.value(),
            "Bad Request",
            errorCode,
            ex.getMessage(),
            correlationId,
            request.getRequestURI()
        );
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }

    
    @ExceptionHandler({EventNotFoundException.class, VenueNotFoundException.class})
    public ResponseEntity<ErrorResponse> handleNotFoundException(
            RuntimeException ex, HttpServletRequest request) {
        String correlationId = UUID.randomUUID().toString();
        logger.warn("Resource not found [{}]: {}", correlationId, ex.getMessage());
        
        String errorCode = ex instanceof EventNotFoundException ? 
            "EVENT_NOT_FOUND" : "VENUE_NOT_FOUND";
        
        ErrorResponse error = new ErrorResponse(
            Instant.now(),
            HttpStatus.NOT_FOUND.value(),
            "Not Found",
            errorCode,
            ex.getMessage(),
            correlationId,
            request.getRequestURI()
        );
        
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler({PublishingException.class, DataAccessException.class})
    public ResponseEntity<ErrorResponse> handleInfrastructureException(
            Exception ex, HttpServletRequest request) {
        String correlationId = UUID.randomUUID().toString();
        logger.error("Infrastructure error [{}]: {}", correlationId, ex.getMessage(), ex);
        
        String errorCode = ex instanceof PublishingException ? 
            "EVENT_PUBLISHING_ERROR" : "DATABASE_ERROR";
        
        ErrorResponse error = new ErrorResponse(
            Instant.now(),
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            "Internal Server Error",
            errorCode,
            "An unexpected error occurred. Please try again later.",
            correlationId,
            request.getRequestURI()
        );
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

### Transaction Management

The service uses Spring's `@Transactional` annotation to ensure data consistency:

**Transaction Boundaries**:
- All use case implementations are transactional
- Database operations and EventBridge publishing occur within the same transaction
- If EventBridge publishing fails, the database transaction is rolled back
- Read-only operations use `@Transactional(readOnly = true)` for optimization

**Rollback Strategy**:
```java
@Service
@Transactional
public class PublishEventService implements PublishEventUseCase {
    
    @Override
    public Event execute(PublishEventCommand command) {
        // 1. Load event from database
        Event event = eventRepository.findById(command.eventId())
            .orElseThrow(() -> new EventNotFoundException(command.eventId()));
        
        // 2. Apply domain logic
        event.publish();
        
        // 3. Save to database
        Event savedEvent = eventRepository.save(event);
        
        // 4. Publish to EventBridge
        try {
            eventPublisher.publish(createDomainEvent(savedEvent));
        } catch (PublishingException e) {
            // Transaction will automatically rollback
            throw new EventPublishingFailedException(e);
        }
        
        // 5. Transaction commits if no exception
        return savedEvent;
    }
}
```

### Retry Strategy

EventBridge publishing uses Spring Retry with exponential backoff:

```java
@Retryable(
    maxAttempts = 3,
    backoff = @Backoff(delay = 1000, multiplier = 2),
    retryFor = {PublishingException.class}
)
public void publish(DomainEvent event) throws PublishingException {
    // Publishing logic
}
```

**Retry Configuration**:
- Maximum 3 attempts
- Initial delay: 1 second
- Backoff multiplier: 2x (1s, 2s, 4s)
- Only retries on PublishingException

### Logging Strategy

**Log Levels**:
- **ERROR**: Infrastructure failures, unexpected exceptions
- **WARN**: Domain rule violations, validation errors, resource not found
- **INFO**: Successful operations, state transitions
- **DEBUG**: Detailed execution flow (development only)

**Structured Logging**:
```java
logger.info("Event created: eventId={}, name={}, venueId={}, status={}", 
    event.getId(), event.getName(), event.getVenueId(), event.getStatus());

logger.warn("Invalid state transition: eventId={}, currentStatus={}, attemptedAction={}", 
    event.getId(), event.getStatus(), "PUBLISH");

logger.error("EventBridge publishing failed: eventId={}, correlationId={}, error={}", 
    event.getId(), correlationId, e.getMessage(), e);
```

**Correlation IDs**:
- Generated for every request
- Included in all log entries
- Returned in error responses
- Enables end-to-end tracing across services

## Testing Strategy

The Event Service employs a dual testing approach combining unit tests for specific scenarios and property-based tests for comprehensive validation of universal properties.

### Testing Philosophy

**Unit Tests**: Focus on specific examples, edge cases, and integration points between components. Unit tests validate concrete scenarios and ensure components work correctly in isolation.

**Property-Based Tests**: Validate universal properties across all possible inputs through randomization. Property tests ensure correctness guarantees hold for the entire input space, not just hand-picked examples.

Together, these approaches provide comprehensive coverage: unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across all inputs.

### Property-Based Testing

**Library**: [jqwik](https://jqwik.net/) - A property-based testing framework for Java

**Configuration**: Each property test runs a minimum of 100 iterations with randomized inputs to ensure comprehensive coverage.

**Test Structure**: Each property test references its corresponding design document property using a comment tag.

**Tag Format**: `// Feature: event-service, Property {number}: {property_text}`

#### Example Property Tests

```java
class EventPropertiesTest {
    
    @Property(tries = 100)
    // Feature: event-service, Property 1: Event Creation Completeness
    void eventCreationShouldIncludeAllRequiredFields(
            @ForAll @StringLength(min = 1, max = 200) String name,
            @ForAll @StringLength(max = 2000) String description,
            @ForAll EventType type,
            @ForAll UUID venueId,
            @ForAll @Future LocalDateTime eventDate,
            @ForAll @IntRange(min = 1, max = 10000) int capacity,
            @ForAll @BigRange(min = "0", max = "10000") BigDecimal price) {
        
        // Arrange
        when(venueRepository.findById(any())).thenReturn(
            Optional.of(createVenue(venueId, capacity + 1000))
        );
        
        CreateEventCommand command = new CreateEventCommand(
            name, description, type, new VenueId(venueId),
            new EventDate(eventDate), new Capacity(capacity),
            new Price(price, "USD")
        );
        
        // Act
        Event event = createEventService.execute(command);
        
        // Assert
        assertThat(event.getId()).isNotNull();
        assertThat(event.getName()).isEqualTo(name);
        assertThat(event.getDescription()).isEqualTo(description);
        assertThat(event.getType()).isEqualTo(type);
        assertThat(event.getVenueId().value()).isEqualTo(venueId);
        assertThat(event.getEventDate().value()).isEqualTo(eventDate);
        assertThat(event.getTotalCapacity().value()).isEqualTo(capacity);
        assertThat(event.getAvailableCapacity().value()).isEqualTo(capacity);
        assertThat(event.getPrice().amount()).isEqualByComparingTo(price);
    }

    
    @Property(tries = 100)
    // Feature: event-service, Property 2: New Events Start in DRAFT Status
    void newlyCreatedEventsShouldHaveDraftStatus(
            @ForAll @StringLength(min = 1, max = 200) String name,
            @ForAll EventType type,
            @ForAll UUID venueId) {
        
        // Arrange
        when(venueRepository.findById(any())).thenReturn(
            Optional.of(createVenue(venueId, 5000))
        );
        
        CreateEventCommand command = createValidCommand(name, type, venueId);
        
        // Act
        Event event = createEventService.execute(command);
        
        // Assert
        assertThat(event.getStatus()).isEqualTo(EventStatus.DRAFT);
    }
    
    @Property(tries = 100)
    // Feature: event-service, Property 3: Initial Capacity Invariant
    void newEventAvailableCapacityShouldEqualTotalCapacity(
            @ForAll @IntRange(min = 1, max = 10000) int capacity) {
        
        // Arrange
        when(venueRepository.findById(any())).thenReturn(
            Optional.of(createVenue(UUID.randomUUID(), capacity + 1000))
        );
        
        CreateEventCommand command = createValidCommandWithCapacity(capacity);
        
        // Act
        Event event = createEventService.execute(command);
        
        // Assert
        assertThat(event.getAvailableCapacity().value())
            .isEqualTo(event.getTotalCapacity().value());
    }
    
    @Property(tries = 100)
    // Feature: event-service, Property 20: Persistence Round Trip
    void persistedEventShouldPreserveAllAttributes(@ForAll Event event) {
        // Act
        Event saved = eventRepository.save(event);
        Event retrieved = eventRepository.findById(saved.getId()).orElseThrow();
        
        // Assert
        assertThat(retrieved).isEqualTo(saved);
        assertThat(retrieved.getName()).isEqualTo(saved.getName());
        assertThat(retrieved.getDescription()).isEqualTo(saved.getDescription());
        assertThat(retrieved.getType()).isEqualTo(saved.getType());
        assertThat(retrieved.getVenueId()).isEqualTo(saved.getVenueId());
        assertThat(retrieved.getEventDate()).isEqualTo(saved.getEventDate());
        assertThat(retrieved.getTotalCapacity()).isEqualTo(saved.getTotalCapacity());
        assertThat(retrieved.getAvailableCapacity()).isEqualTo(saved.getAvailableCapacity());
        assertThat(retrieved.getPrice()).isEqualTo(saved.getPrice());
        assertThat(retrieved.getStatus()).isEqualTo(saved.getStatus());
    }
}
```

### Unit Testing

Unit tests focus on specific scenarios, edge cases, and component integration.

#### Domain Layer Tests

```java
class EventTest {
    
    @Test
    void shouldCreateEventInDraftStatus() {
        Event event = Event.create(
            "Summer Festival",
            "Annual music festival",
            EventType.CONCERT,
            new VenueId(UUID.randomUUID()),
            new EventDate(LocalDateTime.now().plusDays(30)),
            new Capacity(5000),
            new Price(BigDecimal.valueOf(75), "USD")
        );
        
        assertThat(event.getStatus()).isEqualTo(EventStatus.DRAFT);
    }
    
    @Test
    void shouldTransitionFromDraftToPublished() {
        Event event = createDraftEvent();
        
        event.publish();
        
        assertThat(event.getStatus()).isEqualTo(EventStatus.PUBLISHED);
    }
    
    @Test
    void shouldThrowExceptionWhenPublishingNonDraftEvent() {
        Event event = createPublishedEvent();
        
        assertThatThrownBy(() -> event.publish())
            .isInstanceOf(InvalidEventStateException.class)
            .hasMessageContaining("Only DRAFT events can be published");
    }
    
    @Test
    void shouldAllowFullUpdateForDraftEvents() {
        Event event = createDraftEvent();
        
        event.updateDetails("New Name", "New Description", 
            new Price(BigDecimal.valueOf(100), "USD"));
        
        assertThat(event.getName()).isEqualTo("New Name");
        assertThat(event.getDescription()).isEqualTo("New Description");
        assertThat(event.getPrice().amount()).isEqualByComparingTo(BigDecimal.valueOf(100));
    }
    
    @Test
    void shouldOnlyAllowDescriptionAndPriceUpdateForPublishedEvents() {
        Event event = createPublishedEvent();
        String originalName = event.getName();
        
        event.updateDetails("New Name", "New Description", 
            new Price(BigDecimal.valueOf(100), "USD"));
        
        assertThat(event.getName()).isEqualTo(originalName); // Name unchanged
        assertThat(event.getDescription()).isEqualTo("New Description");
        assertThat(event.getPrice().amount()).isEqualByComparingTo(BigDecimal.valueOf(100));
    }
}
```

#### Application Layer Tests

```java
@ExtendWith(MockitoExtension.class)
class CreateEventServiceTest {
    
    @Mock
    private EventRepository eventRepository;
    
    @Mock
    private VenueRepository venueRepository;
    
    @InjectMocks
    private CreateEventService createEventService;
    
    @Test
    void shouldCreateEventSuccessfully() {
        // Arrange
        Venue venue = createVenue(5000);
        when(venueRepository.findById(any())).thenReturn(Optional.of(venue));
        when(eventRepository.save(any())).thenAnswer(i -> i.getArgument(0));
        
        CreateEventCommand command = createValidCommand();
        
        // Act
        Event event = createEventService.execute(command);
        
        // Assert
        assertThat(event).isNotNull();
        assertThat(event.getStatus()).isEqualTo(EventStatus.DRAFT);
        verify(eventRepository).save(any(Event.class));
    }
    
    @Test
    void shouldThrowExceptionWhenVenueNotFound() {
        // Arrange
        when(venueRepository.findById(any())).thenReturn(Optional.empty());
        CreateEventCommand command = createValidCommand();
        
        // Act & Assert
        assertThatThrownBy(() -> createEventService.execute(command))
            .isInstanceOf(VenueNotFoundException.class);
        
        verify(eventRepository, never()).save(any());
    }
    
    @Test
    void shouldThrowExceptionWhenCapacityExceedsVenueMaximum() {
        // Arrange
        Venue venue = createVenue(1000);
        when(venueRepository.findById(any())).thenReturn(Optional.of(venue));
        
        CreateEventCommand command = createCommandWithCapacity(2000);
        
        // Act & Assert
        assertThatThrownBy(() -> createEventService.execute(command))
            .isInstanceOf(CapacityExceededException.class)
            .hasMessageContaining("exceeds venue maximum capacity");
    }
}
```

@ExtendWith(MockitoExtension.class)
class PublishEventServiceTest {
    
    @Mock
    private EventRepository eventRepository;
    
    @Mock
    private EventPublisher eventPublisher;
    
    @InjectMocks
    private PublishEventService publishEventService;
    
    @Test
    void shouldPublishEventAndSendDomainEvent() throws PublishingException {
        // Arrange
        Event draftEvent = createDraftEvent();
        when(eventRepository.findById(any())).thenReturn(Optional.of(draftEvent));
        when(eventRepository.save(any())).thenAnswer(i -> i.getArgument(0));
        
        PublishEventCommand command = new PublishEventCommand(draftEvent.getId());
        
        // Act
        Event publishedEvent = publishEventService.execute(command);
        
        // Assert
        assertThat(publishedEvent.getStatus()).isEqualTo(EventStatus.PUBLISHED);
        verify(eventPublisher).publish(any(EventCreated.class));
    }
    
    @Test
    void shouldRollbackWhenEventBridgePublishingFails() throws PublishingException {
        // Arrange
        Event draftEvent = createDraftEvent();
        when(eventRepository.findById(any())).thenReturn(Optional.of(draftEvent));
        doThrow(new PublishingException("EventBridge unavailable"))
            .when(eventPublisher).publish(any());
        
        PublishEventCommand command = new PublishEventCommand(draftEvent.getId());
        
        // Act & Assert
        assertThatThrownBy(() -> publishEventService.execute(command))
            .isInstanceOf(EventPublishingFailedException.class);
        
        // Transaction should rollback, so save is never committed
        verify(eventRepository).save(any());
    }
}
```

#### Infrastructure Layer Tests

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class PostgresEventRepositoryAdapterTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("eventdb")
        .withUsername("test")
        .withPassword("test");
    
    @Autowired
    private JpaEventRepository jpaRepository;
    
    private PostgresEventRepositoryAdapter adapter;
    
    @BeforeEach
    void setUp() {
        adapter = new PostgresEventRepositoryAdapter(jpaRepository, new EventMapper());
    }
    
    @Test
    void shouldSaveAndRetrieveEvent() {
        // Arrange
        Event event = createDraftEvent();
        
        // Act
        Event saved = adapter.save(event);
        Optional<Event> retrieved = adapter.findById(saved.getId());
        
        // Assert
        assertThat(retrieved).isPresent();
        assertThat(retrieved.get().getId()).isEqualTo(saved.getId());
        assertThat(retrieved.get().getName()).isEqualTo(saved.getName());
    }
    
    @Test
    void shouldFindPublishedEvents() {
        // Arrange
        adapter.save(createDraftEvent());
        adapter.save(createPublishedEvent());
        adapter.save(createPublishedEvent());
        
        // Act
        List<Event> published = adapter.findByStatus(EventStatus.PUBLISHED);
        
        // Assert
        assertThat(published).hasSize(2);
        assertThat(published).allMatch(e -> e.getStatus() == EventStatus.PUBLISHED);
    }
}
```

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class EventControllerTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @MockBean
    private CreateEventUseCase createEventUseCase;
    
    @Test
    void shouldCreateEventAndReturn201() {
        // Arrange
        Event event = createDraftEvent();
        when(createEventUseCase.execute(any())).thenReturn(event);
        
        CreateEventRequest request = new CreateEventRequest(
            "Summer Festival",
            "Annual music festival",
            EventType.CONCERT,
            UUID.randomUUID(),
            LocalDateTime.now().plusDays(30),
            5000,
            BigDecimal.valueOf(75),
            "USD"
        );
        
        // Act
        ResponseEntity<EventResponse> response = restTemplate.postForEntity(
            "/api/v1/events",
            request,
            EventResponse.class
        );
        
        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().name()).isEqualTo("Summer Festival");
    }
    
    @Test
    void shouldReturn400ForInvalidRequest() {
        // Arrange
        CreateEventRequest request = new CreateEventRequest(
            "", // Invalid: empty name
            "Description",
            EventType.CONCERT,
            UUID.randomUUID(),
            LocalDateTime.now().plusDays(30),
            5000,
            BigDecimal.valueOf(75),
            "USD"
        );
        
        // Act
        ResponseEntity<ErrorResponse> response = restTemplate.postForEntity(
            "/api/v1/events",
            request,
            ErrorResponse.class
        );
        
        // Assert
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().errorCode()).isEqualTo("VALIDATION_ERROR");
    }
}
```

### Integration Testing

Integration tests validate the service working with real infrastructure components using Testcontainers and LocalStack.

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class EventServiceIntegrationTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("eventdb");
    
    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:latest"))
        .withServices(LocalStackContainer.Service.EVENTBRIDGE);
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Autowired
    private EventRepository eventRepository;
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("aws.eventbridge.endpoint", 
            () -> localstack.getEndpointOverride(LocalStackContainer.Service.EVENTBRIDGE));
    }
    
    @Test
    void shouldCreatePublishAndRetrieveEvent() {
        // 1. Create venue
        CreateVenueRequest venueRequest = new CreateVenueRequest(
            "Madison Square Garden",
            "4 Pennsylvania Plaza",
            "New York",
            "USA",
            20000
        );
        
        ResponseEntity<VenueResponse> venueResponse = restTemplate.postForEntity(
            "/api/v1/venues",
            venueRequest,
            VenueResponse.class
        );
        
        assertThat(venueResponse.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        UUID venueId = venueResponse.getBody().id();
        
        // 2. Create event
        CreateEventRequest eventRequest = new CreateEventRequest(
            "Summer Music Festival",
            "Annual outdoor music festival",
            EventType.CONCERT,
            venueId,
            LocalDateTime.now().plusDays(60),
            15000,
            BigDecimal.valueOf(75),
            "USD"
        );
        
        ResponseEntity<EventResponse> eventResponse = restTemplate.postForEntity(
            "/api/v1/events",
            eventRequest,
            EventResponse.class
        );
        
        assertThat(eventResponse.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        UUID eventId = eventResponse.getBody().id();
        
        // 3. Publish event
        ResponseEntity<EventResponse> publishResponse = restTemplate.postForEntity(
            "/api/v1/events/" + eventId + "/publish",
            null,
            EventResponse.class
        );
        
        assertThat(publishResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(publishResponse.getBody().status()).isEqualTo(EventStatus.PUBLISHED);
        
        // 4. Retrieve event details
        ResponseEntity<EventDetailsResponse> detailsResponse = restTemplate.getForEntity(
            "/api/v1/events/" + eventId,
            EventDetailsResponse.class
        );
        
        assertThat(detailsResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(detailsResponse.getBody().event().name()).isEqualTo("Summer Music Festival");
        assertThat(detailsResponse.getBody().venue().name()).isEqualTo("Madison Square Garden");
        
        // 5. List published events
        ResponseEntity<EventResponse[]> listResponse = restTemplate.getForEntity(
            "/api/v1/events",
            EventResponse[].class
        );
        
        assertThat(listResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(listResponse.getBody()).hasSize(1);
        assertThat(listResponse.getBody()[0].id()).isEqualTo(eventId);
    }
}
```

### Test Coverage Goals

**Domain Layer**: 100% coverage
- All business rules and invariants
- State transitions
- Value object validation

**Application Layer**: 95%+ coverage
- All use case implementations
- Error handling paths
- Transaction boundaries

**Infrastructure Layer**: 80%+ coverage
- Adapter implementations
- REST controllers
- Database operations
- EventBridge publishing

### Testing Dependencies

```xml
<dependencies>
    <!-- Property-Based Testing -->
    <dependency>
        <groupId>net.jqwik</groupId>
        <artifactId>jqwik</artifactId>
        <version>1.8.2</version>
        <scope>test</scope>
    </dependency>
    
    <!-- Unit Testing -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-junit-jupiter</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <scope>test</scope>
    </dependency>
    
    <!-- Integration Testing -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>localstack</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### Test Execution

```bash
# Run all tests
./mvnw test

# Run only unit tests
./mvnw test -Dgroups="unit"

# Run only property-based tests
./mvnw test -Dgroups="property"

# Run only integration tests
./mvnw test -Dgroups="integration"

# Run tests with coverage report
./mvnw test jacoco:report

# View coverage report
open target/site/jacoco/index.html
```

### Continuous Integration

Tests run automatically on every commit and pull request:

1. **Unit Tests**: Fast feedback (< 30 seconds)
2. **Property Tests**: Comprehensive validation (1-2 minutes)
3. **Integration Tests**: Full system validation (2-3 minutes)

**CI Pipeline**:
```yaml
test:
  stage: test
  script:
    - ./mvnw clean test
    - ./mvnw jacoco:report
  coverage: '/Total.*?([0-9]{1,3})%/'
  artifacts:
    reports:
      junit: target/surefire-reports/TEST-*.xml
      coverage_report:
        coverage_format: jacoco
        path: target/site/jacoco/jacoco.xml
```

## LocalStack Configuration

### Application Configuration

**application-local.yml**:
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:4566/eventdb
    username: test
    password: test
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: true
    properties:
      hibernate:
        format_sql: true
  flyway:
    enabled: true
    locations: classpath:db/migration

aws:
  region: us-east-1
  endpoint: http://localhost:4566
  eventbridge:
    bus-name: event-management-bus
  credentials:
    access-key: test
    secret-key: test

logging:
  level:
    com.eventmanagement: DEBUG
    org.hibernate.SQL: DEBUG
```

### AWS Configuration

```java
@Configuration
@Profile("local")
public class LocalStackConfig {
    
    @Value("${aws.endpoint}")
    private String awsEndpoint;
    
    @Value("${aws.region}")
    private String awsRegion;
    
    @Bean
    public EventBridgeClient eventBridgeClient() {
        return EventBridgeClient.builder()
            .endpointOverride(URI.create(awsEndpoint))
            .region(Region.of(awsRegion))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create("test", "test")
            ))
            .build();
    }
}
```

### Database Initialization

The service uses Flyway for database schema management. On startup, Flyway automatically applies migrations.

**V1__create_venues_table.sql**:
```sql
CREATE TABLE venues (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    max_capacity INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_max_capacity CHECK (max_capacity > 0)
);

CREATE INDEX idx_venues_name ON venues(name);
CREATE INDEX idx_venues_city ON venues(city);
```

**V2__create_events_table.sql**:
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    venue_id UUID NOT NULL,
    event_date TIMESTAMP NOT NULL,
    total_capacity INTEGER NOT NULL,
    available_capacity INTEGER NOT NULL,
    price_amount DECIMAL(10, 2) NOT NULL,
    price_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_venue FOREIGN KEY (venue_id) REFERENCES venues(id),
    CONSTRAINT chk_capacity CHECK (available_capacity >= 0 AND available_capacity <= total_capacity),
    CONSTRAINT chk_price CHECK (price_amount >= 0),
    CONSTRAINT chk_status CHECK (status IN ('DRAFT', 'PUBLISHED', 'CANCELLED'))
);

CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_venue ON events(venue_id);
```

### EventBridge Setup

The service requires an EventBridge event bus to be created in LocalStack:

```bash
# Create event bus
awslocal events create-event-bus --name event-management-bus

# Verify event bus exists
awslocal events list-event-buses

# Create rule to log all events (for debugging)
awslocal events put-rule \
  --name log-all-events \
  --event-bus-name event-management-bus \
  --event-pattern '{"source":["event-service"]}'

# Put events to test
awslocal events put-events \
  --entries '[{
    "Source": "event-service",
    "DetailType": "EventCreated",
    "Detail": "{\"eventId\":\"123\"}",
    "EventBusName": "event-management-bus"
  }]'
```

### Docker Compose Integration

The Event Service can be added to the docker-compose.yml for local development:

```yaml
services:
  localstack:
    # ... existing LocalStack configuration
  
  event-service:
    build: ./event-service
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=local
      - AWS_ENDPOINT=http://localstack:4566
      - AWS_REGION=us-east-1
      - SPRING_DATASOURCE_URL=jdbc:postgresql://localstack:4566/eventdb
    depends_on:
      - localstack
    networks:
      - event-management
```

## Development Workflow

### Initial Setup

1. **Start LocalStack**:
   ```bash
   docker-compose up -d
   ```

2. **Create EventBridge Bus**:
   ```bash
   awslocal events create-event-bus --name event-management-bus
   ```

3. **Run the Service**:
   ```bash
   cd event-service
   ./mvnw spring-boot:run -Dspring-boot.run.profiles=local
   ```

4. **Verify Service Health**:
   ```bash
   curl http://localhost:8080/actuator/health
   ```

### API Testing Examples

**Create a Venue**:
```bash
curl -X POST http://localhost:8080/api/v1/venues \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Madison Square Garden",
    "address": "4 Pennsylvania Plaza",
    "city": "New York",
    "country": "USA",
    "maxCapacity": 20000
  }'
```

**Create an Event**:
```bash
curl -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Summer Music Festival",
    "description": "Annual outdoor music festival",
    "type": "CONCERT",
    "venueId": "550e8400-e29b-41d4-a716-446655440000",
    "eventDate": "2024-07-15T18:00:00",
    "totalCapacity": 15000,
    "priceAmount": 75.00,
    "priceCurrency": "USD"
  }'
```

**Publish an Event**:
```bash
curl -X POST http://localhost:8080/api/v1/events/{eventId}/publish
```

**List Published Events**:
```bash
curl http://localhost:8080/api/v1/events
```

**Get Event Details**:
```bash
curl http://localhost:8080/api/v1/events/{eventId}
```

**Check Availability**:
```bash
curl http://localhost:8080/api/v1/events/{eventId}/availability
```

**Update Event**:
```bash
curl -X PUT http://localhost:8080/api/v1/events/{eventId} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Event Name",
    "description": "Updated description",
    "priceAmount": 85.00
  }'
```

**Cancel Event**:
```bash
curl -X DELETE http://localhost:8080/api/v1/events/{eventId}
```

## Summary

The Event Service design implements Hexagonal Architecture to maintain clean separation between business logic and infrastructure concerns. The domain layer contains pure business logic with no framework dependencies, while adapters handle all external interactions (REST API, PostgreSQL, EventBridge).

Key design decisions:
- **Hexagonal Architecture** ensures testability and maintainability
- **Value Objects** enforce invariants at the type level
- **Domain Events** enable loose coupling with other services
- **Transaction Management** ensures consistency between database and event publishing
- **Property-Based Testing** validates correctness across all inputs
- **LocalStack Integration** enables local development without AWS costs

The service is ready for implementation following this design, with clear boundaries between layers and comprehensive testing strategy to ensure correctness.
