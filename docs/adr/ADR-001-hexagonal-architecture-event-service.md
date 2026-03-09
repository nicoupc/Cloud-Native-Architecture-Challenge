# ADR-001: Hexagonal Architecture for Event Service

## Status

Accepted

## Context

The Event Service needs to isolate business logic from infrastructure concerns such as PostgreSQL, EventBridge, and REST APIs. The team required high testability of domain logic and the ability to swap infrastructure adapters without modifying core business rules. A clear architectural pattern was needed to enforce dependency inversion and maintain separation of concerns as the service evolves.

## Decision

Use Hexagonal Architecture (Ports & Adapters) with three distinct layers:

- **Domain layer**: Contains the `Event` aggregate, value objects, and domain logic. Has no dependencies on infrastructure.
- **Application layer**: Contains application services that orchestrate use cases. Depends only on domain and port interfaces.
- **Infrastructure layer**: Contains adapters for JPA (PostgreSQL), EventBridge (event publishing), and REST (HTTP API). Implements port interfaces defined in the domain/application layers.

Dependency flow is strictly inward: infrastructure → application → domain.

## Consequences

- **Clean dependency inversion** via port interfaces (`EventRepository`, `EventPublisher`) allows the domain to remain infrastructure-agnostic.
- **Domain is fully testable** without spinning up databases, message brokers, or HTTP servers.
- **Adapter swappability**: Infrastructure adapters (e.g., switching from PostgreSQL to another datastore) can be replaced without touching business logic.
- **Trade-off**: Slightly more boilerplate code due to port interfaces and adapter implementations, but this is offset by significantly better maintainability and testability.
- **Onboarding**: New developers must understand the hexagonal pattern, but the clear layer boundaries make the codebase easier to navigate once understood.
