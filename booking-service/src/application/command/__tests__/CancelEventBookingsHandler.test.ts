import { CancelEventBookingsHandler, EventCancelledPayload } from '../CancelEventBookingsHandler';
import { AvailabilityRepository } from '../../../domain/port/AvailabilityRepository';
import { BookingRepository } from '../../../domain/port/BookingRepository';
import { BookingQueryRepository } from '../../../domain/port/BookingQueryRepository';
import { EventPublisher } from '../../../domain/port/EventPublisher';
import { EventAvailability } from '../../../domain/model/EventAvailability';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';

describe('CancelEventBookingsHandler', () => {
  let handler: CancelEventBookingsHandler;
  let mockAvailabilityRepo: jest.Mocked<AvailabilityRepository>;
  let mockBookingQueryRepo: jest.Mocked<BookingQueryRepository>;
  let mockBookingRepo: jest.Mocked<BookingRepository>;
  let mockPublisher: jest.Mocked<EventPublisher>;

  beforeEach(() => {
    mockAvailabilityRepo = {
      save: jest.fn(),
      findByEventId: jest.fn(),
      delete: jest.fn(),
    };

    mockBookingQueryRepo = {
      findById: jest.fn(),
      findByUserId: jest.fn(),
      findByEventId: jest.fn(),
      findAll: jest.fn(),
    };

    mockBookingRepo = {
      save: jest.fn(),
      findById: jest.fn(),
      delete: jest.fn(),
    };

    mockPublisher = {
      publish: jest.fn(),
      publishBatch: jest.fn(),
    };

    handler = new CancelEventBookingsHandler(
      mockAvailabilityRepo,
      mockBookingQueryRepo,
      mockBookingRepo,
      mockPublisher
    );
  });

  it('should deactivate availability and cancel pending bookings', async () => {
    const payload: EventCancelledPayload = {
      eventId: 'event-123',
      reason: 'Weather conditions',
    };

    const availability = EventAvailability.create('event-123', 'Concert', 500, '2024-06-15');
    mockAvailabilityRepo.findByEventId.mockResolvedValue(availability);
    mockAvailabilityRepo.save.mockResolvedValue();

    const booking = Booking.create(
      UserId.from('user-1'),
      EventId.from('event-123'),
      TicketQuantity.from(2),
      50.00
    );
    mockBookingQueryRepo.findByEventId.mockResolvedValue([booking]);
    mockBookingRepo.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    const count = await handler.handle(payload);

    expect(count).toBe(1);
    expect(mockAvailabilityRepo.save).toHaveBeenCalledTimes(1);
    const savedAvailability = mockAvailabilityRepo.save.mock.calls[0][0];
    expect(savedAvailability.active).toBe(false);
    expect(savedAvailability.availableTickets).toBe(0);
    expect(mockBookingRepo.save).toHaveBeenCalledTimes(1);
    expect(mockPublisher.publish).toHaveBeenCalledTimes(1);
    expect(mockPublisher.publish).toHaveBeenCalledWith(
      expect.objectContaining({
        eventType: 'BookingCancelled',
      })
    );
  });

  it('should handle no existing availability', async () => {
    const payload: EventCancelledPayload = {
      eventId: 'event-999',
      reason: 'Cancelled',
    };

    mockAvailabilityRepo.findByEventId.mockResolvedValue(null);
    mockBookingQueryRepo.findByEventId.mockResolvedValue([]);

    const count = await handler.handle(payload);

    expect(count).toBe(0);
    expect(mockAvailabilityRepo.save).not.toHaveBeenCalled();
    expect(mockBookingRepo.save).not.toHaveBeenCalled();
  });

  it('should skip already cancelled bookings', async () => {
    const payload: EventCancelledPayload = {
      eventId: 'event-123',
      reason: 'Cancelled',
    };

    mockAvailabilityRepo.findByEventId.mockResolvedValue(null);

    const booking = Booking.create(
      UserId.from('user-1'),
      EventId.from('event-123'),
      TicketQuantity.from(1),
      25.00
    );
    booking.cancel(); // Already cancelled

    mockBookingQueryRepo.findByEventId.mockResolvedValue([booking]);

    const count = await handler.handle(payload);

    expect(count).toBe(0);
    expect(mockBookingRepo.save).not.toHaveBeenCalled();
    expect(mockPublisher.publish).not.toHaveBeenCalled();
  });

  it('should cancel multiple bookings and publish events for each', async () => {
    const payload: EventCancelledPayload = {
      eventId: 'event-123',
      reason: 'Venue unavailable',
    };

    mockAvailabilityRepo.findByEventId.mockResolvedValue(null);

    const booking1 = Booking.create(
      UserId.from('user-1'),
      EventId.from('event-123'),
      TicketQuantity.from(2),
      50.00
    );
    const booking2 = Booking.create(
      UserId.from('user-2'),
      EventId.from('event-123'),
      TicketQuantity.from(3),
      50.00
    );

    mockBookingQueryRepo.findByEventId.mockResolvedValue([booking1, booking2]);
    mockBookingRepo.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    const count = await handler.handle(payload);

    expect(count).toBe(2);
    expect(mockBookingRepo.save).toHaveBeenCalledTimes(2);
    expect(mockPublisher.publish).toHaveBeenCalledTimes(2);
  });
});
