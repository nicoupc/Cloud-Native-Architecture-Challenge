import { Booking } from '../../domain/model/Booking';
import { BookingId } from '../../domain/model/BookingId';
import { UserId } from '../../domain/model/UserId';
import { EventId } from '../../domain/model/EventId';
import { BookingStatus } from '../../domain/model/BookingStatus';
import { TicketQuantity } from '../../domain/model/TicketQuantity';
import { TotalPrice } from '../../domain/model/TotalPrice';

/**
 * DynamoDB Item structure
 */
export interface DynamoDBBookingItem {
  PK: string;              // BOOKING#{bookingId}
  SK: string;              // BOOKING#{bookingId}
  bookingId: string;
  userId: string;
  eventId: string;
  status: string;
  ticketQuantity: number;
  totalPrice: number;
  createdAt: string;       // ISO format
  updatedAt: string;       // ISO format
}

/**
 * BookingMapper - Converts between Domain and DynamoDB
 * 
 * Why do we need this?
 * - Domain uses Value Objects (BookingId, UserId, etc.)
 * - DynamoDB uses primitive types (string, number)
 * - This mapper translates between both worlds
 * 
 * Hexagonal Architecture:
 * - Domain doesn't know about DynamoDB
 * - Infrastructure knows about both
 */
export class BookingMapper {
  /**
   * Converts Domain Booking to DynamoDB Item
   */
  static toDynamoDB(booking: Booking): DynamoDBBookingItem {
    const bookingId = booking.getId().getValue();

    return {
      // Primary Key (Single Table Design)
      PK: `BOOKING#${bookingId}`,
      SK: `BOOKING#${bookingId}`,

      // Attributes
      bookingId,
      userId: booking.getUserId().getValue(),
      eventId: booking.getEventId().getValue(),
      status: booking.getStatus(),
      ticketQuantity: booking.getTicketQuantity().getValue(),
      totalPrice: booking.getTotalPrice().getAmount(),
      createdAt: booking.getCreatedAt().toISOString(),
      updatedAt: booking.getUpdatedAt().toISOString(),
    };
  }

  /**
   * Converts DynamoDB Item to Domain Booking
   */
  static toDomain(item: DynamoDBBookingItem): Booking {
    return Booking.reconstruct(
      BookingId.from(item.bookingId),
      UserId.from(item.userId),
      EventId.from(item.eventId),
      item.status as BookingStatus,
      TicketQuantity.from(item.ticketQuantity),
      TotalPrice.from(item.totalPrice),
      new Date(item.createdAt),
      new Date(item.updatedAt)
    );
  }
}
