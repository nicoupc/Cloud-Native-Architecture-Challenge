import { v4 as uuidv4 } from 'uuid';
import { DomainEvent } from './DomainEvent';
import { Booking } from '../model/Booking';

/**
 * BookingCancelled - Event emitted when a booking is cancelled
 * 
 * Published to EventBridge for:
 * - Event Service (to release capacity)
 * - Payment Service (to process refund if applicable)
 * - Notification Service (to send cancellation email)
 */
export class BookingCancelled implements DomainEvent {
  readonly eventId: string;
  readonly aggregateId: string;
  readonly eventType = 'BookingCancelled';
  readonly occurredAt: Date;

  constructor(
    readonly userId: string,
    readonly eventIdValue: string,
    readonly reason: string,
    aggregateId: string
  ) {
    this.eventId = uuidv4();
    this.aggregateId = aggregateId;
    this.occurredAt = new Date();
  }

  static from(booking: Booking, reason: string): BookingCancelled {
    return new BookingCancelled(
      booking.getUserId().getValue(),
      booking.getEventId().getValue(),
      reason,
      booking.getId().getValue()
    );
  }
}
