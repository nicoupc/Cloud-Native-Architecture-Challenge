import { GetBookingsByUserHandler } from '../GetBookingsByUserHandler';
import { GetBookingsByUserQuery } from '../../../domain/query/GetBookingsByUserQuery';
import { BookingQueryRepository } from '../../../domain/port/BookingQueryRepository';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';

describe('GetBookingsByUserHandler', () => {
  let handler: GetBookingsByUserHandler;
  let mockQueryRepo: jest.Mocked<BookingQueryRepository>;

  beforeEach(() => {
    mockQueryRepo = {
      findById: jest.fn(),
      findByUserId: jest.fn(),
      findByEventId: jest.fn(),
      findAll: jest.fn(),
    };

    handler = new GetBookingsByUserHandler(mockQueryRepo);
  });

  it('should return bookings for user', async () => {
    // Arrange
    const booking1 = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-1'),
      TicketQuantity.from(2),
      50.00
    );
    const booking2 = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-2'),
      TicketQuantity.from(1),
      75.00
    );
    const query = new GetBookingsByUserQuery('user-123');

    mockQueryRepo.findByUserId.mockResolvedValue([booking1, booking2]);

    // Act
    const result = await handler.handle(query);

    // Assert
    expect(result).toHaveLength(2);
    expect(result[0].getEventId().getValue()).toBe('event-1');
    expect(result[1].getEventId().getValue()).toBe('event-2');
    expect(mockQueryRepo.findByUserId).toHaveBeenCalledTimes(1);
  });

  it('should return empty array when user has no bookings', async () => {
    // Arrange
    const query = new GetBookingsByUserQuery('user-no-bookings');
    mockQueryRepo.findByUserId.mockResolvedValue([]);

    // Act
    const result = await handler.handle(query);

    // Assert
    expect(result).toEqual([]);
    expect(result).toHaveLength(0);
  });
});
