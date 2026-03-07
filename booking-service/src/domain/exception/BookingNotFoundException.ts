import { BookingId } from '../model/BookingId';

/**
 * BookingNotFoundException - Thrown when a booking is not found
 * 
 * HTTP Status: 404 Not Found
 */
export class BookingNotFoundException extends Error {
  constructor(readonly bookingId: BookingId) {
    super(`Booking not found with id: ${bookingId.getValue()}`);
    this.name = 'BookingNotFoundException';
  }
}
