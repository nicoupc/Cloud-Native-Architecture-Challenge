# ADR-002: CQRS with DynamoDB GSI for Booking Service

## Status

Accepted

## Context

The Booking Service exhibits asymmetric read and write patterns. Write operations are transactional in nature (create booking, confirm booking, cancel booking) and require strong consistency. Read operations need optimized queries by different access patterns — primarily by user (to list a user's bookings) and by event (to list all bookings for an event). A traditional relational model would require complex joins or multiple queries to serve these different access patterns efficiently.

## Decision

Implement CQRS (Command Query Responsibility Segregation) using DynamoDB as the backing store:

- **Write model**: Uses the primary key (`bookingId`) for all transactional operations (create, confirm, cancel). Ensures strong consistency for mutations.
- **Read model**: Uses Global Secondary Indexes (GSIs) to serve optimized read queries:
  - `UserBookingsIndex`: GSI on `userId` to efficiently query all bookings for a given user.
  - `EventBookingsIndex`: GSI on `eventId` to efficiently query all bookings for a given event.

A single DynamoDB table serves both the write and read models, with GSIs providing the read-side projections.

## Consequences

- **Eventual consistency** between the write model (base table) and read models (GSIs), as DynamoDB GSIs are eventually consistent by default.
- **Optimized read performance** without complex joins — each access pattern is served by a dedicated index.
- **Single table design** reduces operational complexity compared to maintaining separate read and write datastores.
- **Cost-efficient**: GSIs only project the attributes needed for each read pattern, minimizing storage and read costs.
- **Trade-off**: Adding new access patterns in the future requires creating additional GSIs, which have a per-table limit (20 GSIs per table).
