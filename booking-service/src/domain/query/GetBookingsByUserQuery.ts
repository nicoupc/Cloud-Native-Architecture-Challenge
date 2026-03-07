/**
 * GetBookingsByUserQuery - Query to retrieve all bookings for a user
 * 
 * CQRS Read Side:
 * - Uses DynamoDB GSI: UserBookingsIndex
 * - Optimized for fast user lookups
 * - Returns list of bookings ordered by creation date
 * 
 * Flow:
 * 1. User requests "My Bookings"
 * 2. Creates this query with userId
 * 3. Handler queries GSI (fast!)
 * 4. Returns user's bookings
 */
export class GetBookingsByUserQuery {
  constructor(
    readonly userId: string
  ) {}
}
