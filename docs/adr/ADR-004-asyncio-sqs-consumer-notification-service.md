# ADR-004: Asyncio SQS Consumer over Lambda for Notification Service

## Status

Accepted

## Context

The `challenge.md` specification suggests using AWS Lambda for SQS polling in the Notification Service. However, Lambda introduces additional complexity for local development:

- Lambda requires specific packaging and deployment configuration (ZIP or container image).
- Local Lambda emulation with LocalStack is more complex to set up and debug.
- Lambda cold starts can introduce latency for notification processing.
- Integration testing with Lambda requires additional tooling.

The team prioritized local development experience and debuggability while maintaining functional equivalence with a Lambda-based approach.

## Decision

Use a Python asyncio long-polling consumer instead of AWS Lambda. The consumer:

- Polls SQS with `WaitTimeSeconds=20` (long polling) to minimize empty responses and reduce API calls.
- Processes messages in batches of up to 10 messages per poll cycle.
- Implements token bucket rate limiting to control throughput.
- Supports graceful shutdown via signal handling (SIGTERM, SIGINT).

## Consequences

- **Simpler local development and testing**: The consumer runs as a standard Python process, easily debuggable with standard tools.
- **Functional equivalence**: Messages are processed from SQS with the same end result as a Lambda-based approach.
- **Easier to add cross-cutting concerns**: Rate limiting, graceful shutdown, health checks, and metrics can be added directly to the consumer process.
- **Trade-off — not serverless**: The consumer requires a running process (container), unlike Lambda which scales to zero. This increases baseline infrastructure cost.
- **Production migration path**: In production, this consumer can be migrated to Lambda with an SQS trigger. The message processing logic (handler) is decoupled from the polling mechanism, making this migration straightforward.
