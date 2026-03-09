# ADR-005: Token Bucket Algorithm for Rate Limiting

## Status

Accepted

## Context

The Notification Service needs rate limiting to prevent overwhelming downstream email providers and external notification channels. The rate limiting strategy must:

- Control sustained throughput to stay within provider limits.
- Allow short bursts to handle spike scenarios (e.g., popular event bookings).
- Be simple to implement and configure.
- Work within a single-process consumer (no distributed rate limiting needed for the current scale).

## Decision

Implement the Token Bucket algorithm with the following characteristics:

- **Configurable rate**: Default of 5 messages per second (`RATE_LIMIT_PER_SECOND` environment variable).
- **Configurable burst capacity**: Default of 10 tokens (`RATE_LIMIT_BURST` environment variable).
- **Continuous token refill**: Tokens are added at the configured rate, up to the burst capacity maximum.
- **Blocking consumption**: When no tokens are available, the consumer waits until a token is refilled before processing the next message.

## Consequences

- **Smooth message processing under load**: The token bucket ensures a steady processing rate that respects downstream provider limits.
- **Burst handling**: The burst capacity allows the system to absorb short spikes (up to 10 messages instantly) without dropping or delaying messages unnecessarily.
- **Simple implementation**: The token bucket algorithm is well-understood, easy to implement in Python asyncio, and requires no external dependencies (no Redis or distributed coordination).
- **Runtime configurability**: Rate and burst parameters are configurable via environment variables, allowing operators to tune throughput without code changes.
- **Trade-off**: Single-process rate limiting only. If the Notification Service scales to multiple consumer instances, a distributed rate limiting solution (e.g., Redis-based) would be needed.
