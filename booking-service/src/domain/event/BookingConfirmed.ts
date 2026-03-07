import { v4 as uuidv4 } from 'uuid';
import { DomainEvent } from './DomainEvent';
import { Booking } from '../model/Booking';

/**
 * BookingConfirmed - Event emitted when a booking is confirmed after payment
 * 
 * Published to EventBridge for:
 * - Event Service (to update available capacity)
 * - Notification Service (to send confirmation email)
 * - Analytics Service (to track confirmed bookings)
 */
export class BookingConfirmed implements DomainEvent {
  readonly eventId: string;
  readonly aggregateId: string;
  readonly eventType = 'BookingConfirmed';
  readonly occurredAt: Date;

  constructor(
    readonly userId: string,
    readonly eventIdValue: string,
    readonly ticketQuantity: number,
    aggregateId: string
  ) {
    this.eventId = uuidv4();
    this.aggregateId = aggregateId;
    this.occurredAt = new Date();
  }

  static from(booking: Booking): BookingConfirmed {
    return new BookingConfirmed(
      booking.getUserId().getValue(),
      booking.getEventId().getValue(),
      booking.getTicketQuantity().getValue(),
      booking.getId().getValue()
    );
  }
}
