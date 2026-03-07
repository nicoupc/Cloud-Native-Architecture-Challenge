import { Booking } from '../../../domain/model/Booking';

/**
 * BookingResponse DTO
 * 
 * Converts Domain Booking to API response format
 */

export interface BookingResponse {
  id: string;
  userId: string;
  eventId: string;
  status: string;
  ticketQuantity: number;
  totalPrice: number;
  createdAt: string;
  updatedAt: string;
}

export class BookingResponseMapper {
  static fromDomain(booking: Booking): BookingResponse {
    return {
      id: booking.getId().getValue(),
      userId: booking.getUserId().getValue(),
      eventId: booking.getEventId().getValue(),
      status: booking.getStatus(),
      ticketQuantity: booking.getTicketQuantity().getValue(),
      totalPrice: booking.getTotalPrice().getAmount(),
      createdAt: booking.getCreatedAt().toISOString(),
      updatedAt: booking.getUpdatedAt().toISOString(),
    };
  }

  static fromDomainList(bookings: Booking[]): BookingResponse[] {
    return bookings.map(booking => this.fromDomain(booking));
  }
}
