import { Booking } from '../model/Booking';
import { BookingId } from '../model/BookingId';

/**
 * BookingRepository Port - Write Model (CQRS)
 * 
 * Defines operations for persisting bookings (commands).
 * Optimized for write operations with strong consistency.
 * 
 * Hexagonal Architecture:
 * - Domain defines WHAT it needs (this interface)
 * - Infrastructure implements HOW (DynamoDB adapter)
 */
export interface BookingRepository {
  /**
   * Saves a booking (create or update)
   */
  save(booking: Booking): Promise<Booking>;

  /**
   * Finds a booking by ID
   */
  findById(id: BookingId): Promise<Booking | null>;

  /**
   * Deletes a booking (soft delete recommended)
   */
  delete(id: BookingId): Promise<void>;
}
