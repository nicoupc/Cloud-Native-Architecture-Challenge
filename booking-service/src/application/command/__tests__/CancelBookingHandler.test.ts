import { CancelBookingHandler } from '../CancelBookingHandler';
import { CancelBookingCommand } from '../../../domain/command/CancelBookingCommand';
import { BookingRepository } from '../../../domain/port/BookingRepository';
import { EventPublisher } from '../../../domain/port/EventPublisher';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';
import { BookingStatus } from '../../../domain/model/BookingStatus';
import { BookingNotFoundException } from '../../../domain/exception/BookingNotFoundException';

describe('CancelBookingHandler', () => {
  let handler: CancelBookingHandler;
  let mockRepository: jest.Mocked<BookingRepository>;
  let mockPublisher: jest.Mocked<EventPublisher>;

  beforeEach(() => {
    mockRepository = {
      save: jest.fn(),
      findById: jest.fn(),
      delete: jest.fn(),
    };

    mockPublisher = {
      publish: jest.fn(),
      publishBatch: jest.fn(),
    };

    handler = new CancelBookingHandler(mockRepository, mockPublisher);
  });

  it('should cancel booking successfully from PENDING', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );
    const command = new CancelBookingCommand(booking.getId().getValue(), 'User requested');

    mockRepository.findById.mockResolvedValue(booking);
    mockRepository.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    // Act
    const result = await handler.handle(command);

    // Assert
    expect(result).toBeInstanceOf(Booking);
    expect(result.getStatus()).toBe(BookingStatus.CANCELLED);
  });

  it('should cancel booking successfully from CONFIRMED', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );
    booking.confirm(); // PENDING → CONFIRMED

    const command = new CancelBookingCommand(booking.getId().getValue(), 'Changed plans');

    mockRepository.findById.mockResolvedValue(booking);
    mockRepository.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    // Act
    const result = await handler.handle(command);

    // Assert
    expect(result).toBeInstanceOf(Booking);
    expect(result.getStatus()).toBe(BookingStatus.CANCELLED);
  });

  it('should throw BookingNotFoundException when booking not found', async () => {
    // Arrange
    const command = new CancelBookingCommand('non-existent-id', 'some reason');
    mockRepository.findById.mockResolvedValue(null);

    // Act & Assert
    await expect(handler.handle(command)).rejects.toThrow(BookingNotFoundException);
  });

  it('should save cancelled booking to repository', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(3),
      25.00
    );
    const command = new CancelBookingCommand(booking.getId().getValue(), 'No longer needed');

    mockRepository.findById.mockResolvedValue(booking);
    mockRepository.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    // Act
    await handler.handle(command);

    // Assert
    expect(mockRepository.save).toHaveBeenCalledTimes(1);
    const savedBooking = mockRepository.save.mock.calls[0][0];
    expect(savedBooking.getStatus()).toBe(BookingStatus.CANCELLED);
  });

  it('should publish BookingCancelled event with reason', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );
    const reason = 'Payment failed';
    const command = new CancelBookingCommand(booking.getId().getValue(), reason);

    mockRepository.findById.mockResolvedValue(booking);
    mockRepository.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    // Act
    await handler.handle(command);

    // Assert
    expect(mockPublisher.publish).toHaveBeenCalledTimes(1);
    expect(mockPublisher.publish).toHaveBeenCalledWith(
      expect.objectContaining({
        eventType: 'BookingCancelled',
        userId: 'user-123',
        eventIdValue: 'event-456',
        reason: 'Payment failed',
      })
    );
  });

  it('should throw error when trying to cancel already cancelled booking', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(1),
      100.00
    );
    booking.cancel(); // PENDING → CANCELLED

    const command = new CancelBookingCommand(booking.getId().getValue(), 'Double cancel');
    mockRepository.findById.mockResolvedValue(booking);

    // Act & Assert
    await expect(handler.handle(command)).rejects.toThrow('Invalid status transition');
  });
});
