# ADR-006: EventBridge as Central Event Bus

## Status

Accepted

## Context

The microservices architecture requires asynchronous communication between services for event-driven workflows. The AWS ecosystem offers several messaging options:

- **EventBridge**: Content-based routing with pattern matching, managed event bus.
- **SQS**: Point-to-point message queuing.
- **SNS**: Pub/sub topic-based messaging.

A routing strategy was needed that decouples event producers from consumers, supports filtering by event type, and minimizes operational overhead of managing topic subscriptions.

## Decision

Use Amazon EventBridge as the central event bus for all inter-service communication:

- All services publish domain events to a custom event bus named `event-management-bus`.
- EventBridge rules route events to SQS queues based on `source` and `detail-type` patterns.
- Consumer services poll their dedicated SQS queues for messages.
- **SNS is not used** — EventBridge rules replace the need for SNS topic management and subscription filtering.

Five routing rules connect services to the `notification-queue`:

1. `booking-created` — routes booking creation events.
2. `booking-confirmed` — routes booking confirmation events.
3. `booking-cancelled` — routes booking cancellation events.
4. `payment-completed` — routes successful payment events.
5. `payment-failed` — routes failed payment events.

## Consequences

- **Centralized event routing** with pattern-based filtering simplifies the event flow architecture. New consumers can be added by creating new rules without modifying producers.
- **Decoupled producers and consumers**: Services publish events without knowledge of who consumes them. Routing is managed entirely in EventBridge rules.
- **Events are routable by `source` and `detail-type`**, enabling fine-grained filtering without custom message attributes.
- **Eliminates SNS complexity**: EventBridge rules replace the need to create and manage SNS topics, subscriptions, and filter policies.
- **Trade-off — EventBridge limits**: EventBridge has a payload size limit (256 KB) and rate limits that may require consideration at very high throughput. Sufficient for current scale.
- **Observability**: EventBridge integrates with CloudWatch for monitoring rule invocations and failed deliveries.
