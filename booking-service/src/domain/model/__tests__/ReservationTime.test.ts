import { ReservationTime } from '../ReservationTime';

describe('ReservationTime Value Object', () => {
  describe('from', () => {
    it('should create valid reservation time', () => {
      const start = new Date('2024-01-01T10:00:00Z');
      const end = new Date('2024-01-01T12:00:00Z');

      const reservation = ReservationTime.from(start, end);

      expect(reservation.getStartTime()).toEqual(start);
      expect(reservation.getEndTime()).toEqual(end);
    });

    it('should throw error when startTime is after endTime', () => {
      const start = new Date('2024-01-01T14:00:00Z');
      const end = new Date('2024-01-01T10:00:00Z');

      expect(() => ReservationTime.from(start, end)).toThrow(
        'Start time must be before end time'
      );
    });

    it('should throw error when startTime equals endTime', () => {
      const time = new Date('2024-01-01T10:00:00Z');

      expect(() => ReservationTime.from(time, time)).toThrow(
        'Start time must be before end time'
      );
    });

    it('should throw error for invalid start date', () => {
      const invalidDate = new Date('invalid');
      const end = new Date('2024-01-01T12:00:00Z');

      expect(() => ReservationTime.from(invalidDate, end)).toThrow(
        'Start time must be a valid date'
      );
    });

    it('should throw error for invalid end date', () => {
      const start = new Date('2024-01-01T10:00:00Z');
      const invalidDate = new Date('invalid');

      expect(() => ReservationTime.from(start, invalidDate)).toThrow(
        'End time must be a valid date'
      );
    });
  });

  describe('getDurationInHours', () => {
    it('should calculate duration correctly', () => {
      const start = new Date('2024-01-01T10:00:00Z');
      const end = new Date('2024-01-01T12:00:00Z');

      const reservation = ReservationTime.from(start, end);

      expect(reservation.getDurationInHours()).toBe(2);
    });

    it('should handle fractional hours', () => {
      const start = new Date('2024-01-01T10:00:00Z');
      const end = new Date('2024-01-01T11:30:00Z');

      const reservation = ReservationTime.from(start, end);

      expect(reservation.getDurationInHours()).toBe(1.5);
    });
  });

  describe('overlaps', () => {
    it('should detect overlapping reservations', () => {
      const reservation1 = ReservationTime.from(
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-01T14:00:00Z')
      );
      const reservation2 = ReservationTime.from(
        new Date('2024-01-01T12:00:00Z'),
        new Date('2024-01-01T16:00:00Z')
      );

      expect(reservation1.overlaps(reservation2)).toBe(true);
      expect(reservation2.overlaps(reservation1)).toBe(true);
    });

    it('should detect non-overlapping reservations', () => {
      const reservation1 = ReservationTime.from(
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-01T12:00:00Z')
      );
      const reservation2 = ReservationTime.from(
        new Date('2024-01-01T14:00:00Z'),
        new Date('2024-01-01T16:00:00Z')
      );

      expect(reservation1.overlaps(reservation2)).toBe(false);
      expect(reservation2.overlaps(reservation1)).toBe(false);
    });

    it('should not overlap when one ends exactly as the other starts', () => {
      const reservation1 = ReservationTime.from(
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-01T12:00:00Z')
      );
      const reservation2 = ReservationTime.from(
        new Date('2024-01-01T12:00:00Z'),
        new Date('2024-01-01T14:00:00Z')
      );

      expect(reservation1.overlaps(reservation2)).toBe(false);
    });

    it('should detect when one reservation fully contains another', () => {
      const outer = ReservationTime.from(
        new Date('2024-01-01T08:00:00Z'),
        new Date('2024-01-01T18:00:00Z')
      );
      const inner = ReservationTime.from(
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-01T14:00:00Z')
      );

      expect(outer.overlaps(inner)).toBe(true);
      expect(inner.overlaps(outer)).toBe(true);
    });
  });

  describe('equals', () => {
    it('should return true for equal reservation times', () => {
      const start = new Date('2024-01-01T10:00:00Z');
      const end = new Date('2024-01-01T12:00:00Z');

      const reservation1 = ReservationTime.from(start, end);
      const reservation2 = ReservationTime.from(
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-01T12:00:00Z')
      );

      expect(reservation1.equals(reservation2)).toBe(true);
    });

    it('should return false for different reservation times', () => {
      const reservation1 = ReservationTime.from(
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-01T12:00:00Z')
      );
      const reservation2 = ReservationTime.from(
        new Date('2024-01-01T10:00:00Z'),
        new Date('2024-01-01T14:00:00Z')
      );

      expect(reservation1.equals(reservation2)).toBe(false);
    });
  });

  describe('toString', () => {
    it('should format as ISO string range', () => {
      const start = new Date('2024-01-01T10:00:00Z');
      const end = new Date('2024-01-01T12:00:00Z');

      const reservation = ReservationTime.from(start, end);

      expect(reservation.toString()).toBe(
        '2024-01-01T10:00:00.000Z - 2024-01-01T12:00:00.000Z'
      );
    });
  });
});
