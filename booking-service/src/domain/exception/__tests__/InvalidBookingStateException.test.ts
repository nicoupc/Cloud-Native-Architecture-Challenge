import { InvalidBookingStateException } from '../InvalidBookingStateException';
import { BookingStatus } from '../../model/BookingStatus';

describe('InvalidBookingStateException', () => {
  it('should create exception with correct message', () => {
    const exception = new InvalidBookingStateException(
      BookingStatus.CANCELLED,
      BookingStatus.CONFIRMED
    );

    expect(exception.message).toContain('CANCELLED');
    expect(exception.message).toContain('CONFIRMED');
    expect(exception.name).toBe('InvalidBookingStateException');
  });

  it('should store current and attempted status', () => {
    const exception = new InvalidBookingStateException(
      BookingStatus.CONFIRMED,
      BookingStatus.PENDING
    );

    expect(exception.currentStatus).toBe(BookingStatus.CONFIRMED);
    expect(exception.attemptedStatus).toBe(BookingStatus.PENDING);
  });

  it('should be instance of Error', () => {
    const exception = new InvalidBookingStateException(
      BookingStatus.CANCELLED,
      BookingStatus.CONFIRMED
    );

    expect(exception).toBeInstanceOf(Error);
  });
});
