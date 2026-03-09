import { ConfirmBookingHandler } from '../ConfirmBookingHandler';
import { ConfirmBookingCommand } from '../../../domain/command/ConfirmBookingCommand';
import { BookingRepository } from '../../../domain/port/BookingRepository';
import { EventPublisher } from '../../../domain/port/EventPublisher';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';
import { BookingStatus } from '../../../domain/model/BookingStatus';
import { BookingNotFoundException } from '../../../domain/exception/BookingNotFoundException';

describe('ConfirmBookingHandler', () => {
  let handler: ConfirmBookingHandler;
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

    handler = new ConfirmBookingHandler(mockRepository, mockPublisher);
  });

  it('should confirm booking successfully (PENDING → CONFIRMED)', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );
    const bookingId = booking.getId().getValue();
    const command = new ConfirmBookingCommand(bookingId);

    mockRepository.findById.mockResolvedValue(booking);
    mockRepository.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    // Act
    const result = await handler.handle(command);

    // Assert
    expect(result).toBeInstanceOf(Booking);
    expect(result.getStatus()).toBe(BookingStatus.CONFIRMED);
  });

  it('should throw BookingNotFoundException when booking not found', async () => {
    // Arrange
    const command = new ConfirmBookingCommand('non-existent-id');
    mockRepository.findById.mockResolvedValue(null);

    // Act & Assert
    await expect(handler.handle(command)).rejects.toThrow(BookingNotFoundException);
  });

  it('should save confirmed booking to repository', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(3),
      25.00
    );
    const command = new ConfirmBookingCommand(booking.getId().getValue());

    mockRepository.findById.mockResolvedValue(booking);
    mockRepository.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    // Act
    await handler.handle(command);

    // Assert
    expect(mockRepository.save).toHaveBeenCalledTimes(1);
    expect(mockRepository.save).toHaveBeenCalledWith(
      expect.objectContaining({})
    );
    const savedBooking = mockRepository.save.mock.calls[0][0];
    expect(savedBooking.getStatus()).toBe(BookingStatus.CONFIRMED);
  });

  it('should publish BookingConfirmed event', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );
    const command = new ConfirmBookingCommand(booking.getId().getValue());

    mockRepository.findById.mockResolvedValue(booking);
    mockRepository.save.mockImplementation(async (b) => b);
    mockPublisher.publish.mockResolvedValue();

    // Act
    await handler.handle(command);

    // Assert
    expect(mockPublisher.publish).toHaveBeenCalledTimes(1);
    expect(mockPublisher.publish).toHaveBeenCalledWith(
      expect.objectContaining({
        eventType: 'BookingConfirmed',
        userId: 'user-123',
        eventIdValue: 'event-456',
        ticketQuantity: 2,
      })
    );
  });

  it('should throw error when trying to confirm already cancelled booking', async () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(1),
      100.00
    );
    booking.cancel(); // PENDING → CANCELLED

    const command = new ConfirmBookingCommand(booking.getId().getValue());
    mockRepository.findById.mockResolvedValue(booking);

    // Act & Assert
    await expect(handler.handle(command)).rejects.toThrow('Invalid status transition');
  });
});
