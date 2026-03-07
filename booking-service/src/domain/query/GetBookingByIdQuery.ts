/**
 * GetBookingByIdQuery - Query to retrieve a booking by ID
 * 
 * CQRS Read Side:
 * - Represents the intention to read a booking
 * - Does NOT modify any data
 * - Uses optimized read model
 * 
 * Flow:
 * 1. User requests booking details
 * 2. Creates this query
 * 3. GetBookingByIdHandler retrieves from read model
 * 4. Returns booking data
 */
export class GetBookingByIdQuery {
  constructor(
    readonly bookingId: string
  ) {}
}
