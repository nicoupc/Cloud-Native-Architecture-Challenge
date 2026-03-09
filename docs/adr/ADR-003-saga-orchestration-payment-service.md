# ADR-003: Saga Orchestration over Choreography for Payment Service

## Status

Accepted

## Context

The payment flow requires a coordinated multi-service distributed transaction spanning several steps: reserve booking → process payment → confirm booking → notify user. If any step fails, previous steps must be compensated (rolled back). Two patterns were considered:

- **Choreography**: Each service reacts to events and publishes its own events. No central coordinator.
- **Orchestration**: A central orchestrator directs the saga steps and handles compensation.

Choreography was rejected because the payment flow has a strict sequential ordering and compensation logic that becomes difficult to trace and debug across multiple independent services.

## Decision

Use the Saga Orchestration pattern where the Payment Service acts as the central orchestrator. A state machine tracks saga progress through well-defined states:

```
STARTED → BOOKING_RESERVED → PAYMENT_PROCESSED → BOOKING_CONFIRMED → COMPLETED
```

On failure at any step, the orchestrator triggers compensation actions to reverse previously completed steps (e.g., cancel booking reservation, issue payment refund).

## Consequences

- **Central point of control** for the distributed transaction makes the flow explicit and easy to reason about.
- **Clear compensation flow**: Each state transition has a defined rollback action, ensuring data consistency across services on failure.
- **Easier debugging and monitoring**: The saga state machine provides a single view of transaction progress, making it straightforward to identify where failures occur.
- **Trade-off — single point of coordination**: The Payment Service becomes a critical dependency for the payment flow. If it fails, in-flight sagas may stall. This is mitigated by persisting saga state in DynamoDB and supporting saga recovery on restart.
- **Trade-off — tighter coupling**: The orchestrator must know about the steps involved, creating some coupling to the participating services' APIs.
