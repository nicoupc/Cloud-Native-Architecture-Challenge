import { DomainEvent } from '../event/DomainEvent';

/**
 * EventPublisher Port
 * 
 * Defines how to publish domain events to the event bus.
 * 
 * Hexagonal Architecture:
 * - Domain defines WHAT it needs (this interface)
 * - Infrastructure implements HOW (EventBridge adapter)
 */
export interface EventPublisher {
  /**
   * Publishes a domain event to EventBridge
   */
  publish(event: DomainEvent): Promise<void>;

  /**
   * Publishes multiple domain events in batch
   */
  publishBatch(events: DomainEvent[]): Promise<void>;
}
