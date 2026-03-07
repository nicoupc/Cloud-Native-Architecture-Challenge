import { CreateBookingCommand } from '../../domain/command/CreateBookingCommand';
import { Booking } from '../../domain/model/Booking';
import { UserId } from '../../domain/model/UserId';
import { EventId } from '../../domain/model/EventId';
import { TicketQuantity } from '../../domain/model/TicketQuantity';
import { BookingRepository } from '../../domain/port/BookingRepository';
import { EventPublisher } from '../../domain/port/EventPublisher';
import { BookingCreated } from '../../domain/event/BookingCreated';

/**
 * CreateBookingHandler - Handles the creation of new bookings
 * 
 * CQRS Command Handler (Write Side):
 * - Receives CreateBookingCommand
 * - Executes business logic
 * - Persists to write model
 * - Publishes domain event
 * 
 * Responsibilities:
 * 1. Validate command data
 * 2. Create Booking aggregate
 * 3. Save to repository (write model)
 * 4. Publish BookingCreated event
 * 
 * Flow:
 * REST API → Command → Handler → Domain → Repository → EventBridge
 */
export class CreateBookingHandler {
  constructor(
    private readonly bookingRepository: BookingRepository,
    private readonly eventPublisher: EventPublisher
  ) {}

  async handle(command: CreateBookingCommand): Promise<Booking> {
    // 1. Convert command data to Value Objects
    const userId = UserId.from(command.userId);
    const eventId = EventId.from(command.eventId);
    const ticketQuantity = TicketQuantity.from(command.ticketQuantity);

    // 2. Create Booking aggregate (domain logic)
    const booking = Booking.create(
      userId,
      eventId,
      ticketQuantity,
      command.pricePerTicket
    );

    // 3. Save to repository (write model)
    const savedBooking = await this.bookingRepository.save(booking);

    // 4. Publish domain event (async communication)
    const event = BookingCreated.from(savedBooking);
    await this.eventPublisher.publish(event);

    return savedBooking;
  }
}
