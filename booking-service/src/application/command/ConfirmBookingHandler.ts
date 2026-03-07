import { ConfirmBookingCommand } from '../../domain/command/ConfirmBookingCommand';
import { Booking } from '../../domain/model/Booking';
import { BookingId } from '../../domain/model/BookingId';
import { BookingRepository } from '../../domain/port/BookingRepository';
import { EventPublisher } from '../../domain/port/EventPublisher';
import { BookingConfirmed } from '../../domain/event/BookingConfirmed';
import { BookingNotFoundException } from '../../domain/exception/BookingNotFoundException';

/**
 * ConfirmBookingHandler - Handles booking confirmation after payment
 * 
 * CQRS Command Handler (Write Side):
 * - Receives ConfirmBookingCommand
 * - Transitions booking to CONFIRMED
 * - Publishes BookingConfirmed event
 * 
 * Responsibilities:
 * 1. Load booking from repository
 * 2. Call booking.confirm() (domain logic)
 * 3. Save updated booking
 * 4. Publish BookingConfirmed event
 * 
 * Flow:
 * Payment Service → Command → Handler → Domain → Repository → EventBridge
 */
export class ConfirmBookingHandler {
  constructor(
    private readonly bookingRepository: BookingRepository,
    private readonly eventPublisher: EventPublisher
  ) {}

  async handle(command: ConfirmBookingCommand): Promise<Booking> {
    // 1. Load booking from repository
    const bookingId = BookingId.from(command.bookingId);
    const booking = await this.bookingRepository.findById(bookingId);

    if (!booking) {
      throw new BookingNotFoundException(bookingId);
    }

    // 2. Execute domain logic (state transition)
    booking.confirm();

    // 3. Save updated booking
    const confirmedBooking = await this.bookingRepository.save(booking);

    // 4. Publish domain event
    const event = BookingConfirmed.from(confirmedBooking);
    await this.eventPublisher.publish(event);

    return confirmedBooking;
  }
}
