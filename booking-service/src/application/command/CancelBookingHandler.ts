import { CancelBookingCommand } from '../../domain/command/CancelBookingCommand';
import { Booking } from '../../domain/model/Booking';
import { BookingId } from '../../domain/model/BookingId';
import { BookingRepository } from '../../domain/port/BookingRepository';
import { EventPublisher } from '../../domain/port/EventPublisher';
import { BookingCancelled } from '../../domain/event/BookingCancelled';
import { BookingNotFoundException } from '../../domain/exception/BookingNotFoundException';

/**
 * CancelBookingHandler - Handles booking cancellation
 * 
 * CQRS Command Handler (Write Side):
 * - Receives CancelBookingCommand
 * - Transitions booking to CANCELLED
 * - Publishes BookingCancelled event
 * 
 * Responsibilities:
 * 1. Load booking from repository
 * 2. Call booking.cancel() (domain logic)
 * 3. Save updated booking
 * 4. Publish BookingCancelled event
 * 
 * Triggered by:
 * - User cancellation request
 * - Payment failure (saga compensation)
 * 
 * Flow:
 * User/Payment Service → Command → Handler → Domain → Repository → EventBridge
 */
export class CancelBookingHandler {
  constructor(
    private readonly bookingRepository: BookingRepository,
    private readonly eventPublisher: EventPublisher
  ) {}

  async handle(command: CancelBookingCommand): Promise<Booking> {
    // 1. Load booking from repository
    const bookingId = BookingId.from(command.bookingId);
    const booking = await this.bookingRepository.findById(bookingId);

    if (!booking) {
      throw new BookingNotFoundException(bookingId);
    }

    // 2. Execute domain logic (state transition)
    booking.cancel();

    // 3. Save updated booking
    const cancelledBooking = await this.bookingRepository.save(booking);

    // 4. Publish domain event
    const event = BookingCancelled.from(cancelledBooking, command.reason);
    await this.eventPublisher.publish(event);

    return cancelledBooking;
  }
}
