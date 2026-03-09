import { BookingId } from './BookingId';
import { UserId } from './UserId';
import { EventId } from './EventId';
import { BookingStatus, BookingStatusTransition } from './BookingStatus';
import { TicketQuantity } from './TicketQuantity';
import { TotalPrice } from './TotalPrice';

/**
 * Booking Aggregate Root
 * 
 * Represents a ticket booking with its complete lifecycle.
 * Enforces all business rules and invariants.
 */
export class Booking {
  private constructor(
    private readonly id: BookingId,
    private readonly userId: UserId,
    private readonly eventId: EventId,
    private status: BookingStatus,
    private readonly ticketQuantity: TicketQuantity,
    private readonly totalPrice: TotalPrice,
    private readonly createdAt: Date,
    private updatedAt: Date
  ) {}

  /**
   * Factory method: Creates a new booking in PENDING status
   */
  static create(
    userId: UserId,
    eventId: EventId,
    ticketQuantity: TicketQuantity,
    pricePerTicket: number
  ): Booking {
    const totalPrice = TotalPrice.calculate(
      ticketQuantity.getValue(),
      pricePerTicket
    );

    const now = new Date();

    return new Booking(
      BookingId.generate(),
      userId,
      eventId,
      BookingStatus.PENDING,
      ticketQuantity,
      totalPrice,
      now,
      now
    );
  }

  /**
   * Reconstruction method: Rebuilds booking from persistence
   */
  static reconstruct(
    id: BookingId,
    userId: UserId,
    eventId: EventId,
    status: BookingStatus,
    ticketQuantity: TicketQuantity,
    totalPrice: TotalPrice,
    createdAt: Date,
    updatedAt: Date
  ): Booking {
    return new Booking(
      id,
      userId,
      eventId,
      status,
      ticketQuantity,
      totalPrice,
      createdAt,
      updatedAt
    );
  }

  /**
   * Business method: Confirms the booking after successful payment
   */
  confirm(): void {
    BookingStatusTransition.validateTransition(
      this.status,
      BookingStatus.CONFIRMED
    );
    this.status = BookingStatus.CONFIRMED;
    this.updatedAt = new Date();
  }

  /**
   * Business method: Cancels the booking
   */
  cancel(): void {
    BookingStatusTransition.validateTransition(
      this.status,
      BookingStatus.CANCELLED
    );
    this.status = BookingStatus.CANCELLED;
    this.updatedAt = new Date();
  }

  // Getters
  getId(): BookingId {
    return this.id;
  }

  getUserId(): UserId {
    return this.userId;
  }

  getEventId(): EventId {
    return this.eventId;
  }

  getStatus(): BookingStatus {
    return this.status;
  }

  getTicketQuantity(): TicketQuantity {
    return this.ticketQuantity;
  }

  getTotalPrice(): TotalPrice {
    return this.totalPrice;
  }

  getCreatedAt(): Date {
    return this.createdAt;
  }

  getUpdatedAt(): Date {
    return this.updatedAt;
  }

  /**
   * Checks if booking can be cancelled
   */
  canBeCancelled(): boolean {
    return this.status !== BookingStatus.CANCELLED;
  }
}
