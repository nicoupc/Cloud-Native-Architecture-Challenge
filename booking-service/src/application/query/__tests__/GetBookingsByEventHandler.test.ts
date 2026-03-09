import { GetBookingsByEventHandler } from '../GetBookingsByEventHandler';
import { GetBookingsByEventQuery } from '../../../domain/query/GetBookingsByEventQuery';
import { BookingQueryRepository } from '../../../domain/port/BookingQueryRepository';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';

describe('GetBookingsByEventHandler', () => {
  let handler: GetBookingsByEventHandler;
  let mockQueryRepo: jest.Mocked<BookingQueryRepository>;

  beforeEach(() => {
    mockQueryRepo = {
      findById: jest.fn(),
      findByUserId: jest.fn(),
      findByEventId: jest.fn(),
      findAll: jest.fn(),
    };

    handler = new GetBookingsByEventHandler(mockQueryRepo);
  });

  it('should return bookings for event', async () => {
    // Arrange
    const booking1 = Booking.create(
      UserId.from('user-1'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );
    const booking2 = Booking.create(
      UserId.from('user-2'),
      EventId.from('event-456'),
      TicketQuantity.from(4),
      50.00
    );
    const query = new GetBookingsByEventQuery('event-456');

    mockQueryRepo.findByEventId.mockResolvedValue([booking1, booking2]);

    // Act
    const result = await handler.handle(query);

    // Assert
    expect(result).toHaveLength(2);
    expect(result[0].getUserId().getValue()).toBe('user-1');
    expect(result[1].getUserId().getValue()).toBe('user-2');
    expect(mockQueryRepo.findByEventId).toHaveBeenCalledTimes(1);
  });

  it('should return empty array when event has no bookings', async () => {
    // Arrange
    const query = new GetBookingsByEventQuery('event-no-bookings');
    mockQueryRepo.findByEventId.mockResolvedValue([]);

    // Act
    const result = await handler.handle(query);

    // Assert
    expect(result).toEqual([]);
    expect(result).toHaveLength(0);
  });
});
