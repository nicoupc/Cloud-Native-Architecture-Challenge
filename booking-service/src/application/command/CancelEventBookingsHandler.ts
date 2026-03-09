import { AvailabilityRepository } from '../../domain/port/AvailabilityRepository';
import { BookingRepository } from '../../domain/port/BookingRepository';
import { BookingQueryRepository } from '../../domain/port/BookingQueryRepository';
import { EventPublisher } from '../../domain/port/EventPublisher';
import { BookingCancelled } from '../../domain/event/BookingCancelled';
import { EventId } from '../../domain/model/EventId';

export interface EventCancelledPayload {
  eventId: string;
  reason: string;
}

export class CancelEventBookingsHandler {
  constructor(
    private readonly availabilityRepository: AvailabilityRepository,
    private readonly bookingQueryRepository: BookingQueryRepository,
    private readonly bookingRepository: BookingRepository,
    private readonly eventPublisher: EventPublisher
  ) {}

  async handle(payload: EventCancelledPayload): Promise<number> {
    // 1. Deactivate availability
    const availability = await this.availabilityRepository.findByEventId(payload.eventId);
    if (availability) {
      availability.deactivate();
      await this.availabilityRepository.save(availability);
    }

    // 2. Find and cancel all active bookings for this event
    const bookings = await this.bookingQueryRepository.findByEventId(EventId.from(payload.eventId));
    let cancelledCount = 0;

    for (const booking of bookings) {
      if (booking.canBeCancelled()) {
        booking.cancel();
        await this.bookingRepository.save(booking);
        const event = BookingCancelled.from(booking, `Event cancelled: ${payload.reason}`);
        await this.eventPublisher.publish(event);
        cancelledCount++;
      }
    }

    return cancelledCount;
  }
}
