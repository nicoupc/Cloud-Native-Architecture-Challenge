import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { DynamoDBBookingRepository } from '../DynamoDBBookingRepository';
import { Booking } from '../../../domain/model/Booking';
import { BookingId } from '../../../domain/model/BookingId';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';

jest.mock('@aws-sdk/lib-dynamodb', () => {
  const actual = jest.requireActual('@aws-sdk/lib-dynamodb');
  return {
    ...actual,
    DynamoDBDocumentClient: {
      from: jest.fn(),
    },
    PutCommand: jest.fn(),
    GetCommand: jest.fn(),
    DeleteCommand: jest.fn(),
  };
});

describe('DynamoDBBookingRepository', () => {
  let repository: DynamoDBBookingRepository;
  let mockSend: jest.Mock;

  beforeEach(() => {
    mockSend = jest.fn();
    (DynamoDBDocumentClient.from as jest.Mock).mockReturnValue({ send: mockSend });
    const mockClient = {} as DynamoDBClient;
    repository = new DynamoDBBookingRepository(mockClient, 'TestBookings');
  });

  describe('save', () => {
    it('should save booking and return it', async () => {
      mockSend.mockResolvedValue({});
      const booking = Booking.create(
        UserId.from('user-123'),
        EventId.from('event-456'),
        TicketQuantity.from(2),
        50.00
      );

      const result = await repository.save(booking);

      expect(mockSend).toHaveBeenCalledTimes(1);
      expect(result).toBe(booking);
    });
  });

  describe('findById', () => {
    it('should return booking when found', async () => {
      const bookingId = 'test-booking-id';
      mockSend.mockResolvedValue({
        Item: {
          PK: `BOOKING#${bookingId}`,
          SK: `BOOKING#${bookingId}`,
          bookingId,
          userId: 'user-123',
          eventId: 'event-456',
          status: 'PENDING',
          ticketQuantity: 2,
          totalPrice: 100,
          createdAt: '2024-01-01T00:00:00.000Z',
          updatedAt: '2024-01-01T00:00:00.000Z',
        },
      });

      const result = await repository.findById(BookingId.from(bookingId));

      expect(result).toBeInstanceOf(Booking);
      expect(result!.getId().getValue()).toBe(bookingId);
    });

    it('should return null when not found', async () => {
      mockSend.mockResolvedValue({ Item: undefined });

      const result = await repository.findById(BookingId.from('non-existent'));

      expect(result).toBeNull();
    });
  });

  describe('delete', () => {
    it('should delete booking by id', async () => {
      mockSend.mockResolvedValue({});

      await repository.delete(BookingId.from('booking-to-delete'));

      expect(mockSend).toHaveBeenCalledTimes(1);
    });
  });
});
