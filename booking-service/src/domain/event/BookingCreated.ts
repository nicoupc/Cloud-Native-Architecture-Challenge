import { v4 as uuidv4 } from 'uuid';
import { DomainEvent } from './DomainEvent';
import { Booking } from '../model/Booking';

/**
 * BookingCreated - Event emitted when a new booking is created
 * 
 * Published to EventBridge for:
 * - Payment Service (to initiate payment saga)
 * - Notification Service (to send confirmation email)
 * - Analytics Service (to track booking metrics)
 */
export class BookingCreated implements DomainEvent {
  readonly eventId: string;
  readonly aggregateId: string;
  readonly eventType = 'BookingCreated';
  readonly occurredAt: Date;

  constructor(
    readonly userId: string,
    readonly eventIdValue: string,
    readonly ticketQuantity: number,
    readonly totalPrice: number,
    readonly currency: string,
    aggregateId: string
  ) {
    this.eventId = uuidv4();
    this.aggregateId = aggregateId;
    this.occurredAt = new Date();
  }

  static from(booking: Booking): BookingCreated {
    return new BookingCreated(
      booking.getUserId().getValue(),
      booking.getEventId().getValue(),
      booking.getTicketQuantity().getValue(),
      booking.getTotalPrice().getAmount(),
      booking.getTotalPrice().getCurrency(),
      booking.getId().getValue()
    );
  }
}
