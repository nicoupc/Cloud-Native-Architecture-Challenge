import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand, QueryCommand, ScanCommand } from '@aws-sdk/lib-dynamodb';
import { BookingQueryRepository } from '../../domain/port/BookingQueryRepository';
import { Booking } from '../../domain/model/Booking';
import { BookingId } from '../../domain/model/BookingId';
import { UserId } from '../../domain/model/UserId';
import { EventId } from '../../domain/model/EventId';
import { BookingMapper, DynamoDBBookingItem } from './BookingMapper';

/**
 * DynamoDBBookingQueryRepository - Read Model Adapter
 * 
 * Implements BookingQueryRepository port for DynamoDB.
 * Optimized for read operations using GSI.
 * 
 * CQRS:
 * - This is the READ MODEL
 * - Optimized for queries (findByUserId, findByEventId)
 * - Uses GSI for efficient queries
 * - Eventual consistency is acceptable
 * 
 * GSI Strategy:
 * - UserBookingsIndex: Query bookings by userId
 * - EventBookingsIndex: Query bookings by eventId
 */
export class DynamoDBBookingQueryRepository implements BookingQueryRepository {
  private readonly docClient: DynamoDBDocumentClient;
  private readonly tableName: string;

  constructor(
    dynamoClient: DynamoDBClient,
    tableName: string = 'Bookings'
  ) {
    this.docClient = DynamoDBDocumentClient.from(dynamoClient);
    this.tableName = tableName;
  }

  /**
   * Finds a booking by ID
   * Uses eventual consistency (acceptable for read model)
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
        // ConsistentRead: false (default) - Eventual consistency
      })
    );

    if (!result.Item) {
      return null;
    }

    return BookingMapper.toDomain(result.Item as DynamoDBBookingItem);
  }

  /**
   * Finds all bookings for a user
   * Uses GSI: UserBookingsIndex
   */
  async findByUserId(userId: UserId): Promise<Booking[]> {
    const result = await this.docClient.send(
      new QueryCommand({
        TableName: this.tableName,
        IndexName: 'UserBookingsIndex',
        KeyConditionExpression: 'userId = :userId',
        ExpressionAttributeValues: {
          ':userId': userId.getValue(),
        },
        ScanIndexForward: false, // Sort by createdAt DESC (newest first)
      })
    );

    if (!result.Items || result.Items.length === 0) {
      return [];
    }

    return result.Items.map(item => 
      BookingMapper.toDomain(item as DynamoDBBookingItem)
    );
  }

  /**
   * Finds all bookings for an event
   * Uses GSI: EventBookingsIndex
   */
  async findByEventId(eventId: EventId): Promise<Booking[]> {
    const result = await this.docClient.send(
      new QueryCommand({
        TableName: this.tableName,
        IndexName: 'EventBookingsIndex',
        KeyConditionExpression: 'eventId = :eventId',
        ExpressionAttributeValues: {
          ':eventId': eventId.getValue(),
        },
        ScanIndexForward: false, // Sort by createdAt DESC
      })
    );

    if (!result.Items || result.Items.length === 0) {
      return [];
    }

    return result.Items.map(item => 
      BookingMapper.toDomain(item as DynamoDBBookingItem)
    );
  }

  /**
   * Finds all bookings with pagination
   * Uses Scan (expensive, use with caution in production)
   */
  async findAll(limit: number = 20, lastKey?: string): Promise<{
    bookings: Booking[];
    lastKey?: string;
  }> {
    const result = await this.docClient.send(
      new ScanCommand({
        TableName: this.tableName,
        Limit: limit,
        ExclusiveStartKey: lastKey ? JSON.parse(lastKey) : undefined,
      })
    );

    const bookings = result.Items
      ? result.Items.map(item => BookingMapper.toDomain(item as DynamoDBBookingItem))
      : [];

    return {
      bookings,
      lastKey: result.LastEvaluatedKey 
        ? JSON.stringify(result.LastEvaluatedKey)
        : undefined,
    };
  }
}
