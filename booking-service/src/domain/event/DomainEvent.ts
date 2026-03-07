/**
 * DomainEvent - Base interface for all domain events
 * 
 * Domain events represent facts that have already happened in the domain.
 * They are immutable and communicate changes to other parts of the system.
 */
export interface DomainEvent {
  /**
   * Unique identifier for this event instance
   */
  readonly eventId: string;

  /**
   * ID of the aggregate that generated this event
   */
  readonly aggregateId: string;

  /**
   * Type of the event (for routing in EventBridge)
   */
  readonly eventType: string;

  /**
   * Timestamp when the event occurred
   */
  readonly occurredAt: Date;
}
