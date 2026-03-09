/**
 * Contract Tests: Booking Service Event Schemas
 *
 * Verify that domain events emitted by the Booking Service conform to
 * the schemas expected by downstream consumers (Payment Service,
 * Notification Service, Event Service) via EventBridge.
 */
import { BookingCreated } from '../BookingCreated';
import { BookingConfirmed } from '../BookingConfirmed';
import { BookingCancelled } from '../BookingCancelled';

describe('Event Schema Contract Tests', () => {
  describe('BookingCreated schema', () => {
    let event: BookingCreated;

    beforeEach(() => {
      event = new BookingCreated(
        'user-456',    // userId
        'event-789',   // eventIdValue
        2,             // ticketQuantity
        100.0,         // totalPrice
        'USD',         // currency
        'booking-123', // aggregateId
      );
    });

    it('should have all DomainEvent base fields', () => {
      expect(event.eventId).toBeDefined();
      expect(typeof event.eventId).toBe('string');
      expect(event.aggregateId).toBe('booking-123');
      expect(event.eventType).toBe('BookingCreated');
      expect(event.occurredAt).toBeInstanceOf(Date);
    });

    it('should have userId for notification routing', () => {
      expect(event.userId).toBe('user-456');
    });

    it('should have eventIdValue for event service lookups', () => {
      expect(event.eventIdValue).toBe('event-789');
    });

    it('should have ticketQuantity as a number', () => {
      expect(typeof event.ticketQuantity).toBe('number');
      expect(event.ticketQuantity).toBe(2);
    });

    it('should have totalPrice as a number', () => {
      expect(typeof event.totalPrice).toBe('number');
      expect(event.totalPrice).toBe(100.0);
    });

    it('should have currency as a string', () => {
      expect(typeof event.currency).toBe('string');
      expect(event.currency).toBe('USD');
    });

    it('should have eventType exactly "BookingCreated" for EventBridge routing', () => {
      expect(event.eventType).toBe('BookingCreated');
    });

    it('should generate a unique eventId (UUID)', () => {
      const another = new BookingCreated('u', 'e', 1, 10, 'USD', 'b');
      expect(event.eventId).not.toBe(another.eventId);
    });
  });

  describe('BookingConfirmed schema', () => {
    let event: BookingConfirmed;

    beforeEach(() => {
      event = new BookingConfirmed(
        'user-456',    // userId
        'event-789',   // eventIdValue
        2,             // ticketQuantity
        'booking-123', // aggregateId
      );
    });

    it('should have all DomainEvent base fields', () => {
      expect(event.eventId).toBeDefined();
      expect(typeof event.eventId).toBe('string');
      expect(event.aggregateId).toBe('booking-123');
      expect(event.eventType).toBe('BookingConfirmed');
      expect(event.occurredAt).toBeInstanceOf(Date);
    });

    it('should have userId for notification routing', () => {
      expect(event.userId).toBe('user-456');
    });

    it('should have eventIdValue for event service capacity updates', () => {
      expect(event.eventIdValue).toBe('event-789');
    });

    it('should have ticketQuantity for capacity adjustment', () => {
      expect(typeof event.ticketQuantity).toBe('number');
      expect(event.ticketQuantity).toBe(2);
    });

    it('should have eventType exactly "BookingConfirmed" for EventBridge routing', () => {
      expect(event.eventType).toBe('BookingConfirmed');
    });
  });

  describe('BookingCancelled schema', () => {
    let event: BookingCancelled;

    beforeEach(() => {
      event = new BookingCancelled(
        'user-456',         // userId
        'event-789',        // eventIdValue
        'Payment failed',   // reason
        'booking-123',      // aggregateId
      );
    });

    it('should have all DomainEvent base fields', () => {
      expect(event.eventId).toBeDefined();
      expect(typeof event.eventId).toBe('string');
      expect(event.aggregateId).toBe('booking-123');
      expect(event.eventType).toBe('BookingCancelled');
      expect(event.occurredAt).toBeInstanceOf(Date);
    });

    it('should have userId for notification routing', () => {
      expect(event.userId).toBe('user-456');
    });

    it('should have eventIdValue for event service capacity release', () => {
      expect(event.eventIdValue).toBe('event-789');
    });

    it('should have reason as a string', () => {
      expect(typeof event.reason).toBe('string');
      expect(event.reason).toBe('Payment failed');
    });

    it('should have eventType exactly "BookingCancelled" for EventBridge routing', () => {
      expect(event.eventType).toBe('BookingCancelled');
    });
  });

  describe('Cross-event contract guarantees', () => {
    it('all events implement the DomainEvent interface fields', () => {
      const events = [
        new BookingCreated('u', 'e', 1, 10, 'USD', 'b1'),
        new BookingConfirmed('u', 'e', 1, 'b2'),
        new BookingCancelled('u', 'e', 'reason', 'b3'),
      ];

      events.forEach((event) => {
        expect(event).toHaveProperty('eventId');
        expect(event).toHaveProperty('aggregateId');
        expect(event).toHaveProperty('eventType');
        expect(event).toHaveProperty('occurredAt');
      });
    });

    it('each event type has a distinct eventType string', () => {
      const types = new Set([
        new BookingCreated('u', 'e', 1, 10, 'USD', 'b').eventType,
        new BookingConfirmed('u', 'e', 1, 'b').eventType,
        new BookingCancelled('u', 'e', 'r', 'b').eventType,
      ]);
      expect(types.size).toBe(3);
    });

    it('aggregateId always corresponds to the booking ID', () => {
      expect(new BookingCreated('u', 'e', 1, 10, 'USD', 'my-booking').aggregateId).toBe('my-booking');
      expect(new BookingConfirmed('u', 'e', 1, 'my-booking').aggregateId).toBe('my-booking');
      expect(new BookingCancelled('u', 'e', 'r', 'my-booking').aggregateId).toBe('my-booking');
    });
  });
});
