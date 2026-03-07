/**
 * CreateBookingCommand - Command to create a new booking
 * 
 * CQRS Write Side:
 * - Represents the intention to create a booking
 * - Contains all data needed for the operation
 * - Immutable (readonly)
 * 
 * Flow:
 * 1. REST API receives request
 * 2. Creates this command
 * 3. Passes to CreateBookingHandler
 * 4. Handler executes business logic
 */
export class CreateBookingCommand {
  constructor(
    readonly userId: string,
    readonly eventId: string,
    readonly ticketQuantity: number,
    readonly pricePerTicket: number
  ) {}
}
