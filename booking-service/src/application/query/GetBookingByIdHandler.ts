import { GetBookingByIdQuery } from '../../domain/query/GetBookingByIdQuery';
import { Booking } from '../../domain/model/Booking';
import { BookingId } from '../../domain/model/BookingId';
import { BookingQueryRepository } from '../../domain/port/BookingQueryRepository';
import { BookingNotFoundException } from '../../domain/exception/BookingNotFoundException';

/**
 * GetBookingByIdHandler - Handles booking retrieval by ID
 * 
 * CQRS Query Handler (Read Side):
 * - Receives GetBookingByIdQuery
 * - Retrieves from read model (optimized for queries)
 * - Does NOT modify any data
 * 
 * Responsibilities:
 * 1. Validate query
 * 2. Query read model
 * 3. Return booking data
 * 
 * CQRS Separation:
 * - Uses BookingQueryRepository (read-optimized)
 * - NOT BookingRepository (write-optimized)
 * 
 * Flow:
 * REST API → Query → Handler → Read Model → Response
 */
export class GetBookingByIdHandler {
  constructor(
    private readonly bookingQueryRepository: BookingQueryRepository
  ) {}

  async handle(query: GetBookingByIdQuery): Promise<Booking> {
    const bookingId = BookingId.from(query.bookingId);
    
    const booking = await this.bookingQueryRepository.findById(bookingId);

    if (!booking) {
      throw new BookingNotFoundException(bookingId);
    }

    return booking;
  }
}
