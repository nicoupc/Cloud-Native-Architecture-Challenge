import { CreateBookingHandler } from '../CreateBookingHandler';
import { CreateBookingCommand } from '../../../domain/command/CreateBookingCommand';
import { BookingRepository } from '../../../domain/port/BookingRepository';
import { EventPublisher } from '../../../domain/port/EventPublisher';
import { Booking } from '../../../domain/model/Booking';
import { BookingStatus } from '../../../domain/model/BookingStatus';

describe('CreateBookingHandler', () => {
  let handler: CreateBookingHandler;
  let mockRepository: jest.Mocked<BookingRepository>;
  let mockPublisher: jest.Mocked<EventPublisher>;

  beforeEach(() => {
    // Create mocks
    mockRepository = {
      save: jest.fn(),
      findById: jest.fn(),
      delete: jest.fn(),
    };

    mockPublisher = {
      publish: jest.fn(),
      publishBatch: jest.fn(),
    };

    handler = new CreateBookingHandler(mockRepository, mockPublisher);
  });

  it('should create booking successfully', async () => {
    // Arrange
    const command = new CreateBookingCommand(
      'user-123',
      'event-456',
      3,
      50.00
    );

    mockRepository.save.mockImplementation(async (booking) => booking);
    mockPublisher.publish.mockResolvedValue();

    // Act
    const result = await handler.handle(command);

    // Assert
    expect(result).toBeInstanceOf(Booking);
    expect(result.getStatus()).toBe(BookingStatus.PENDING);
    expect(result.getTicketQuantity().getValue()).toBe(3);
    expect(result.getTotalPrice().getAmount()).toBe(150.00);
    expect(mockRepository.save).toHaveBeenCalledTimes(1);
    expect(mockPublisher.publish).toHaveBeenCalledTimes(1);
  });

  it('should throw error for invalid ticket quantity', async () => {
    // Arrange
    const command = new CreateBookingCommand(
      'user-123',
      'event-456',
      0, // Invalid: less than 1
      50.00
    );

    // Act & Assert
    await expect(handler.handle(command)).rejects.toThrow('must be at least 1');
  });

  it('should publish BookingCreated event', async () => {
    // Arrange
    const command = new CreateBookingCommand(
      'user-123',
      'event-456',
      2,
      50.00
    );

    mockRepository.save.mockImplementation(async (booking) => booking);
    mockPublisher.publish.mockResolvedValue();

    // Act
    await handler.handle(command);

    // Assert
    expect(mockPublisher.publish).toHaveBeenCalledWith(
      expect.objectContaining({
        eventType: 'BookingCreated',
        userId: 'user-123',
        eventIdValue: 'event-456',
      })
    );
  });
});
