import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand, GetCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';
import { AvailabilityRepository } from '../../domain/port/AvailabilityRepository';
import { EventAvailability } from '../../domain/model/EventAvailability';

export class DynamoDBAvailabilityRepository implements AvailabilityRepository {
  private readonly docClient: DynamoDBDocumentClient;

  constructor(
    dynamoClient: DynamoDBClient,
    private readonly tableName: string
  ) {
    this.docClient = DynamoDBDocumentClient.from(dynamoClient);
  }

  async save(availability: EventAvailability): Promise<void> {
    await this.docClient.send(new PutCommand({
      TableName: this.tableName,
      Item: {
        eventId: availability.eventId,
        eventName: availability.eventName,
        totalCapacity: availability.totalCapacity,
        availableTickets: availability.availableTickets,
        eventDate: availability.eventDate,
        active: availability.active,
        updatedAt: new Date().toISOString(),
      },
    }));
  }

  async findByEventId(eventId: string): Promise<EventAvailability | null> {
    const result = await this.docClient.send(new GetCommand({
      TableName: this.tableName,
      Key: { eventId },
    }));

    if (!result.Item) return null;

    return new EventAvailability(
      result.Item.eventId,
      result.Item.eventName,
      result.Item.totalCapacity,
      result.Item.availableTickets,
      result.Item.eventDate,
      result.Item.active
    );
  }

  async delete(eventId: string): Promise<void> {
    await this.docClient.send(new DeleteCommand({
      TableName: this.tableName,
      Key: { eventId },
    }));
  }
}
