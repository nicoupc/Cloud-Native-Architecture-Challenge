import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand, GetCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';
import { BookingRepository } from '../../domain/port/BookingRepository';
import { Booking } from '../../domain/model/Booking';
import { BookingId } from '../../domain/model/BookingId';
import { BookingMapper, DynamoDBBookingItem } from './BookingMapper';

/**
 * DynamoDBBookingRepository - Write Model Adapter
 * 
 * Implements BookingRepository port for DynamoDB.
 * Optimized for write operations (save, delete).
 * 
 * Hexagonal Architecture:
 * - Domain defines the interface (BookingRepository)
 * - Infrastructure implements it (this class)
 * - Domain doesn't know about DynamoDB
 * 
 * CQRS:
 * - This is the WRITE MODEL
 * - Optimized for consistency and validation
 * - Uses strong consistency reads
 */
export class DynamoDBBookingRepository implements BookingRepository {
  private readonly docClient: DynamoDBDocumentClient;
  private readonly tableName: string;

  constructor(
    dynamoClient: DynamoDBClient,
    tableName: string = 'Bookings'
  ) {
    // DynamoDBDocumentClient simplifies working with DynamoDB
    // Automatically converts JS types to DynamoDB types
    this.docClient = DynamoDBDocumentClient.from(dynamoClient);
    this.tableName = tableName;
  }

  /**
   * Saves a booking (create or update)
   * Uses PutItem for upsert behavior
   */
  async save(booking: Booking): Promise<Booking> {
    const item = BookingMapper.toDynamoDB(booking);

    await this.docClient.send(
      new PutCommand({
        TableName: this.tableName,
        Item: item,
      })
    );

    return booking;
  }

  /**
   * Finds a booking by ID
   * Uses strong consistency for write model
   */
  async findById(id: BookingId): Promise<Booking | null> {
    const bookingId = id.getValue();

    const result = await this.docClient.send(
      new GetCommand({
        TableName: this.tableName,
        Key: {
          PK: `BOOKING#${bookingId}`,
          SK: `BOOKING#${bookingId}`,
        },
        ConsistentRead: true, // Strong consistency for write model
      })
    );

    if (!result.Item) {
      return null;
    }

    return BookingMapper.toDomain(result.Item as DynamoDBBookingItem);
  }

  /**
   * Deletes a booking
   * Physical delete (could be soft delete in production)
   */
  async delete(id: BookingId): Promise<void> {
    const bookingId = id.getValue();

    await this.docClient.send(
      new DeleteCommand({
        TableName: this.tableName,
        Key: {
          PK: `BOOKING#${bookingId}`,
          SK: `BOOKING#${bookingId}`,
        },
      })
    );
  }
}
