/**
 * ConfirmBookingCommand - Command to confirm a booking after payment
 * 
 * CQRS Write Side:
 * - Represents the intention to confirm a booking
 * - Triggered by Payment Service after successful payment
 * 
 * Flow:
 * 1. Payment Service processes payment successfully
 * 2. Sends this command to Booking Service
 * 3. ConfirmBookingHandler transitions booking to CONFIRMED
 * 4. Publishes BookingConfirmed event
 */
export class ConfirmBookingCommand {
  constructor(
    readonly bookingId: string
  ) {}
}
