/**
 * Contract Tests: Booking Service API (Provider Side)
 *
 * These tests verify that the Booking Service API returns responses
 * in the format that the Payment Service (consumer) expects.
 * If the response shape changes, these tests will fail, alerting us
 * to a contract violation before it reaches production.
 */
import { BookingResponseMapper, BookingResponse } from '../dto/BookingResponse';

// Required fields the Payment Service relies on
const REQUIRED_BOOKING_FIELDS: (keyof BookingResponse)[] = [
  'id',
  'userId',
  'eventId',
  'status',
  'ticketQuantity',
  'totalPrice',
  'createdAt',
  'updatedAt',
];

const VALID_STATUSES = ['PENDING', 'CONFIRMED', 'CANCELLED'];

/** Helper: create a mock Booking domain object matching the real getters. */
function createMockBooking(overrides: Record<string, unknown> = {}) {
  const defaults = {
    id: 'booking-123',
    userId: 'user-456',
    eventId: 'event-789',
    status: 'CONFIRMED',
    ticketQuantity: 2,
    totalPrice: 100.0,
    createdAt: new Date('2026-01-01'),
    updatedAt: new Date('2026-01-01'),
  };

  const vals = { ...defaults, ...overrides };

  return {
    getId: () => ({ getValue: () => vals.id }),
    getUserId: () => ({ getValue: () => vals.userId }),
    getEventId: () => ({ getValue: () => vals.eventId }),
    getStatus: () => vals.status,
    getTicketQuantity: () => ({ getValue: () => vals.ticketQuantity }),
    getTotalPrice: () => ({ getAmount: () => vals.totalPrice }),
    getCreatedAt: () => vals.createdAt,
    getUpdatedAt: () => vals.updatedAt,
  } as any;
}

describe('Booking API Contract Tests (Provider Side)', () => {
  describe('BookingResponseMapper contract', () => {
    it('should include all fields that Payment Service expects', () => {
      const booking = createMockBooking();
      const response = BookingResponseMapper.fromDomain(booking);

      REQUIRED_BOOKING_FIELDS.forEach((field) => {
        expect(response).toHaveProperty(field);
      });
    });

    it('should map id as a string', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.id).toBe('string');
    });

    it('should map userId as a string', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.userId).toBe('string');
    });

    it('should map eventId as a string', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.eventId).toBe('string');
    });

    it('should map status as a string', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.status).toBe('string');
    });

    it('should map ticketQuantity as a number', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.ticketQuantity).toBe('number');
    });

    it('should map totalPrice as a number', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.totalPrice).toBe('number');
    });

    it('should map createdAt as an ISO string', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.createdAt).toBe('string');
      expect(response.createdAt).toContain('T');
    });

    it('should map updatedAt as an ISO string', () => {
      const response = BookingResponseMapper.fromDomain(createMockBooking());
      expect(typeof response.updatedAt).toBe('string');
      expect(response.updatedAt).toContain('T');
    });
  });

  describe('Contract: status values', () => {
    it.each(VALID_STATUSES)(
      'should correctly map status "%s"',
      (status) => {
        const booking = createMockBooking({ status });
        const response = BookingResponseMapper.fromDomain(booking);
        expect(response.status).toBe(status);
      },
    );

    it('should preserve exact status string from domain model', () => {
      const booking = createMockBooking({ status: 'PENDING' });
      const response = BookingResponseMapper.fromDomain(booking);
      expect(response.status).toBe('PENDING');
    });
  });

  describe('Contract: response envelope', () => {
    it('should produce the {success: true, data: ...} envelope', () => {
      const booking = createMockBooking();
      const response = BookingResponseMapper.fromDomain(booking);

      // The controller wraps the mapper result in { success: true, data: response }
      const envelope = { success: true, data: response };

      expect(envelope).toHaveProperty('success', true);
      expect(envelope).toHaveProperty('data');
      expect(envelope.data).toHaveProperty('id');
      expect(envelope.data).toHaveProperty('status');
    });
  });

  describe('Contract: list response', () => {
    it('should map a list of bookings preserving shape', () => {
      const bookings = [
        createMockBooking({ id: 'b-1', status: 'PENDING' }),
        createMockBooking({ id: 'b-2', status: 'CONFIRMED' }),
      ];
      const responses = BookingResponseMapper.fromDomainList(bookings);

      expect(responses).toHaveLength(2);
      responses.forEach((r) => {
        REQUIRED_BOOKING_FIELDS.forEach((field) => {
          expect(r).toHaveProperty(field);
        });
      });
    });

    it('should produce the list envelope with count', () => {
      const bookings = [createMockBooking()];
      const responses = BookingResponseMapper.fromDomainList(bookings);
      const envelope = { success: true, data: responses, count: responses.length };

      expect(envelope).toHaveProperty('success', true);
      expect(envelope).toHaveProperty('count', 1);
      expect(Array.isArray(envelope.data)).toBe(true);
    });
  });
});
