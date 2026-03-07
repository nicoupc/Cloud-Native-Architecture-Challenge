import { Booking } from '../model/Booking';
import { BookingId } from '../model/BookingId';
import { UserId } from '../model/UserId';
import { EventId } from '../model/EventId';

/**
 * BookingQueryRepository Port - Read Model (CQRS)
 * 
 * Defines operations for querying bookings (queries).
 * Optimized for read operations with eventual consistency.
 * Uses DynamoDB GSI for efficient queries.
 * 
 * CQRS Separation:
 * - BookingRepository: Write operations (save, delete)
 * - BookingQueryRepository: Read operations (find, list)
 */
export interface BookingQueryRepository {
  /**
   * Finds a booking by ID
   */
  findById(id: BookingId): Promise<Booking | null>;

  /**
   * Finds all bookings for a specific user
   * Uses GSI: UserBookingsIndex
   */
  findByUserId(userId: UserId): Promise<Booking[]>;

  /**
   * Finds all bookings for a specific event
   * Uses GSI: EventBookingsIndex
   */
  findByEventId(eventId: EventId): Promise<Booking[]>;

  /**
   * Finds all bookings (with pagination)
   */
  findAll(limit?: number, lastKey?: string): Promise<{
    bookings: Booking[];
    lastKey?: string;
  }>;
}
