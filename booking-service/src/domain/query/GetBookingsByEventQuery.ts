/**
 * GetBookingsByEventQuery - Query to retrieve all bookings for an event
 * 
 * CQRS Read Side:
 * - Uses DynamoDB GSI: EventBookingsIndex
 * - Optimized for event organizers to see all bookings
 * - Returns list of bookings ordered by creation date
 * 
 * Flow:
 * 1. Event organizer requests "Event Bookings"
 * 2. Creates this query with eventId
 * 3. Handler queries GSI (fast!)
 * 4. Returns event's bookings
 */
export class GetBookingsByEventQuery {
  constructor(
    readonly eventId: string
  ) {}
}
