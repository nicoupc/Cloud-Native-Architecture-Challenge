import { EventBridgeClient, PutEventsCommand } from '@aws-sdk/client-eventbridge';
import { EventPublisher } from '../../domain/port/EventPublisher';
import { DomainEvent } from '../../domain/event/DomainEvent';

/**
 * EventBridgePublisher - Adapter for publishing domain events
 * 
 * Implements EventPublisher port using AWS EventBridge.
 * 
 * Hexagonal Architecture:
 * - Domain defines what it needs (EventPublisher interface)
 * - Infrastructure implements how (this class)
 * - Domain doesn't know about EventBridge
 * 
 * Event-Driven Architecture:
 * - Publishes domain events to EventBridge
 * - Other services can subscribe to these events
 * - Enables loose coupling between services
 */
export class EventBridgePublisher implements EventPublisher {
  private readonly client: EventBridgeClient;
  private readonly eventBusName: string;
  private readonly source: string;

  constructor(
    client: EventBridgeClient,
    eventBusName: string = 'event-management-bus',
    source: string = 'booking-service'
  ) {
    this.client = client;
    this.eventBusName = eventBusName;
    this.source = source;
  }

  /**
   * Publishes a domain event to EventBridge
   */
  async publish(event: DomainEvent): Promise<void> {
    const command = new PutEventsCommand({
      Entries: [
        {
          Source: this.source,
          DetailType: event.eventType,
          Detail: JSON.stringify(event),
          EventBusName: this.eventBusName,
          Time: event.occurredAt,
        },
      ],
    });

    const result = await this.client.send(command);

    // Check if event was published successfully
    if (result.FailedEntryCount && result.FailedEntryCount > 0) {
      const error = result.Entries?.[0]?.ErrorMessage || 'Unknown error';
      throw new Error(`Failed to publish event: ${error}`);
    }
  }

  /**
   * Publishes multiple domain events in a batch
   * EventBridge supports up to 10 events per batch
   */
  async publishBatch(events: DomainEvent[]): Promise<void> {
    if (events.length === 0) {
      return;
    }

    // EventBridge limit: 10 events per batch
    const batches = this.chunkArray(events, 10);

    for (const batch of batches) {
      const command = new PutEventsCommand({
        Entries: batch.map(event => ({
          Source: this.source,
          DetailType: event.eventType,
          Detail: JSON.stringify(event),
          EventBusName: this.eventBusName,
          Time: event.occurredAt,
        })),
      });

      const result = await this.client.send(command);

      if (result.FailedEntryCount && result.FailedEntryCount > 0) {
        throw new Error(`Failed to publish ${result.FailedEntryCount} events`);
      }
    }
  }

  /**
   * Helper: Splits array into chunks
   */
  private chunkArray<T>(array: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
}
