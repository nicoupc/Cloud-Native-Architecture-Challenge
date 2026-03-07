import { BookingStatus } from '../model/BookingStatus';

/**
 * InvalidBookingStateException - Thrown when an invalid state transition is attempted
 * 
 * HTTP Status: 400 Bad Request
 */
export class InvalidBookingStateException extends Error {
  constructor(
    readonly currentStatus: BookingStatus,
    readonly attemptedStatus: BookingStatus
  ) {
    super(
      `Invalid booking state transition: ${currentStatus} → ${attemptedStatus}`
    );
    this.name = 'InvalidBookingStateException';
  }
}
