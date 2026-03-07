/**
 * CancelBookingCommand - Command to cancel a booking
 * 
 * CQRS Write Side:
 * - Represents the intention to cancel a booking
 * - Can be triggered by user or by payment failure
 * 
 * Flow:
 * 1. User requests cancellation OR Payment fails
 * 2. Creates this command with reason
 * 3. CancelBookingHandler transitions booking to CANCELLED
 * 4. Publishes BookingCancelled event
 */
export class CancelBookingCommand {
  constructor(
    readonly bookingId: string,
    readonly reason: string
  ) {}
}
