import { BookingStatus, BookingStatusTransition } from '../BookingStatus';

describe('BookingStatus', () => {
  describe('BookingStatusTransition', () => {
    describe('isValidTransition', () => {
      it('should allow PENDING → CONFIRMED', () => {
        expect(
          BookingStatusTransition.isValidTransition(
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED
          )
        ).toBe(true);
      });

      it('should allow PENDING → CANCELLED', () => {
        expect(
          BookingStatusTransition.isValidTransition(
            BookingStatus.PENDING,
            BookingStatus.CANCELLED
          )
        ).toBe(true);
      });

      it('should allow CONFIRMED → CANCELLED', () => {
        expect(
          BookingStatusTransition.isValidTransition(
            BookingStatus.CONFIRMED,
            BookingStatus.CANCELLED
          )
        ).toBe(true);
      });

      it('should NOT allow CANCELLED → CONFIRMED', () => {
        expect(
          BookingStatusTransition.isValidTransition(
            BookingStatus.CANCELLED,
            BookingStatus.CONFIRMED
          )
        ).toBe(false);
      });

      it('should NOT allow CANCELLED → PENDING', () => {
        expect(
          BookingStatusTransition.isValidTransition(
            BookingStatus.CANCELLED,
            BookingStatus.PENDING
          )
        ).toBe(false);
      });

      it('should NOT allow CONFIRMED → PENDING', () => {
        expect(
          BookingStatusTransition.isValidTransition(
            BookingStatus.CONFIRMED,
            BookingStatus.PENDING
          )
        ).toBe(false);
      });
    });

    describe('validateTransition', () => {
      it('should not throw for valid transitions', () => {
        expect(() =>
          BookingStatusTransition.validateTransition(
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED
          )
        ).not.toThrow();
      });

      it('should throw for invalid transitions', () => {
        expect(() =>
          BookingStatusTransition.validateTransition(
            BookingStatus.CANCELLED,
            BookingStatus.CONFIRMED
          )
        ).toThrow('Invalid status transition');
      });
    });
  });
});
