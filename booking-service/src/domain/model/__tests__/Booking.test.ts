import { Booking } from '../Booking';
import { UserId } from '../UserId';
import { EventId } from '../EventId';
import { TicketQuantity } from '../TicketQuantity';
import { BookingStatus } from '../BookingStatus';

describe('Booking Aggregate', () => {
  describe('create', () => {
    it('should create a new booking in PENDING status', () => {
      // Arrange
      const userId = UserId.from('user-123');
      const eventId = EventId.from('event-456');
      const quantity = TicketQuantity.from(3);
      const pricePerTicket = 50.00;

      // Act
      const booking = Booking.create(userId, eventId, quantity, pricePerTicket);

      // Assert
      expect(booking.getUserId()).toEqual(userId);
      expect(booking.getEventId()).toEqual(eventId);
      expect(booking.getTicketQuantity()).toEqual(quantity);
      expect(booking.getTotalPrice().getAmount()).toBe(150.00); // 3 × 50
      expect(booking.getStatus()).toBe(BookingStatus.PENDING);
      expect(booking.getId()).toBeDefined();
      expect(booking.getCreatedAt()).toBeInstanceOf(Date);
    });

    it('should calculate total price correctly', () => {
      const userId = UserId.from('user-123');
      const eventId = EventId.from('event-456');
      const quantity = TicketQuantity.from(5);
      const pricePerTicket = 25.50;

      const booking = Booking.create(userId, eventId, quantity, pricePerTicket);

      expect(booking.getTotalPrice().getAmount()).toBe(127.50); // 5 × 25.50
    });
  });

  describe('confirm', () => {
    it('should transition from PENDING to CONFIRMED', () => {
      // Arrange
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );

      // Act
      booking.confirm();

      // Assert
      expect(booking.getStatus()).toBe(BookingStatus.CONFIRMED);
    });

    it('should throw error when confirming non-PENDING booking', () => {
      // Arrange
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );
      booking.cancel(); // Now it's CANCELLED

      // Act & Assert
      expect(() => booking.confirm()).toThrow('Invalid status transition');
    });
  });

  describe('cancel', () => {
    it('should transition from PENDING to CANCELLED', () => {
      // Arrange
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );

      // Act
      booking.cancel();

      // Assert
      expect(booking.getStatus()).toBe(BookingStatus.CANCELLED);
    });

    it('should transition from CONFIRMED to CANCELLED', () => {
      // Arrange
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );
      booking.confirm();

      // Act
      booking.cancel();

      // Assert
      expect(booking.getStatus()).toBe(BookingStatus.CANCELLED);
    });

    it('should throw error when cancelling already CANCELLED booking', () => {
      // Arrange
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );
      booking.cancel();

      // Act & Assert
      expect(() => booking.cancel()).toThrow('Invalid status transition');
    });
  });

  describe('canBeCancelled', () => {
    it('should return true for PENDING booking', () => {
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );

      expect(booking.canBeCancelled()).toBe(true);
    });

    it('should return true for CONFIRMED booking', () => {
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );
      booking.confirm();

      expect(booking.canBeCancelled()).toBe(true);
    });

    it('should return false for CANCELLED booking', () => {
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );
      booking.cancel();

      expect(booking.canBeCancelled()).toBe(false);
    });
  });
});
