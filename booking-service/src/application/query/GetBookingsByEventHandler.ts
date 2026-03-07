import { GetBookingsByEventQuery } from '../../domain/query/GetBookingsByEventQuery';
import { Booking } from '../../domain/model/Booking';
import { EventId } from '../../domain/model/EventId';
import { BookingQueryRepository } from '../../domain/port/BookingQueryRepository';

/**
 * GetBookingsByEventHandler - Handles retrieval of event's bookings
 * 
 * CQRS Query Handler (Read Side):
 * - Receives GetBookingsByEventQuery
 * - Uses DynamoDB GSI: EventBookingsIndex
 * - Optimized for event organizers
 * 
 * Responsibilities:
 * 1. Validate query
 * 2. Query GSI (fast!)
 * 3. Return list of bookings
 * 
 * Use Cases:
 * - Event organizer views all bookings
 * - Calculate total tickets sold
 * - Generate attendee list
 * 
 * Performance:
 * - GSI allows O(1) lookup by eventId
 * - No table scan needed
 * - Results ordered by creation date
 * 
 * Flow:
 * REST API → Query → Handler → GSI → Response
 */
export class GetBookingsByEventHandler {
  constructor(
    private readonly bookingQueryRepository: BookingQueryRepository
  ) {}

  async handle(query: GetBookingsByEventQuery): Promise<Booking[]> {
    const eventId = EventId.from(query.eventId);
    
    const bookings = await this.bookingQueryRepository.findByEventId(eventId);

    return bookings;
  }
}
