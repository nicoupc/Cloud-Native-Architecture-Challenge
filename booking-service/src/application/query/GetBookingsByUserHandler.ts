import { GetBookingsByUserQuery } from '../../domain/query/GetBookingsByUserQuery';
import { Booking } from '../../domain/model/Booking';
import { UserId } from '../../domain/model/UserId';
import { BookingQueryRepository } from '../../domain/port/BookingQueryRepository';

/**
 * GetBookingsByUserHandler - Handles retrieval of user's bookings
 * 
 * CQRS Query Handler (Read Side):
 * - Receives GetBookingsByUserQuery
 * - Uses DynamoDB GSI: UserBookingsIndex
 * - Optimized for fast user lookups
 * 
 * Responsibilities:
 * 1. Validate query
 * 2. Query GSI (fast!)
 * 3. Return list of bookings
 * 
 * Performance:
 * - GSI allows O(1) lookup by userId
 * - No table scan needed
 * - Results ordered by creation date
 * 
 * Flow:
 * REST API → Query → Handler → GSI → Response
 */
export class GetBookingsByUserHandler {
  constructor(
    private readonly bookingQueryRepository: BookingQueryRepository
  ) {}

  async handle(query: GetBookingsByUserQuery): Promise<Booking[]> {
    const userId = UserId.from(query.userId);
    
    const bookings = await this.bookingQueryRepository.findByUserId(userId);

    return bookings;
  }
}
