import { GetBookingByIdHandler } from '../GetBookingByIdHandler';
import { GetBookingByIdQuery } from '../../../domain/query/GetBookingByIdQuery';
import { BookingQueryRepository } from '../../../domain/port/BookingQueryRepository';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';
import { BookingNotFoundException } from '../../../domain/exception/BookingNotFoundException';

describe('GetBookingByIdHandler', () => {
  let handler: GetBookingByIdHandler;
  let mockQueryRepo: jest.Mocked<BookingQueryRepository>;

  beforeEach(() => {
    mockQueryRepo = {
      findById: jest.fn(),
      findByUserId: jest.fn(),
      findByEventId: jest.fn(),
      findAll: jest.fn(),
    };

    handler = new GetBookingByIdHandler(mockQueryRepo);
  });

  it('should return booking when found', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );
    const query = new GetBookingByIdQuery(booking.getId().getValue());

    mockQueryRepo.findById.mockResolvedValue(booking);

    // Act
    const result = await handler.handle(query);

    // Assert
    expect(result).toBeInstanceOf(Booking);
    expect(result.getUserId().getValue()).toBe('user-123');
    expect(result.getEventId().getValue()).toBe('event-456');
    expect(mockQueryRepo.findById).toHaveBeenCalledTimes(1);
  });

  it('should throw BookingNotFoundException when not found', async () => {
    // Arrange
    const query = new GetBookingByIdQuery('non-existent-id');
    mockQueryRepo.findById.mockResolvedValue(null);

    // Act & Assert
    await expect(handler.handle(query)).rejects.toThrow(BookingNotFoundException);
  });
});
