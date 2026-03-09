import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { DynamoDBBookingQueryRepository } from '../DynamoDBBookingQueryRepository';
import { Booking } from '../../../domain/model/Booking';
import { BookingId } from '../../../domain/model/BookingId';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';

jest.mock('@aws-sdk/lib-dynamodb', () => {
  const actual = jest.requireActual('@aws-sdk/lib-dynamodb');
  return {
    ...actual,
    DynamoDBDocumentClient: {
      from: jest.fn(),
    },
    GetCommand: jest.fn(),
    QueryCommand: jest.fn(),
    ScanCommand: jest.fn(),
  };
});

const sampleItem = {
  PK: 'BOOKING#booking-1',
  SK: 'BOOKING#booking-1',
  bookingId: 'booking-1',
  userId: 'user-123',
  eventId: 'event-456',
  status: 'PENDING',
  ticketQuantity: 2,
  totalPrice: 100,
  createdAt: '2024-01-01T00:00:00.000Z',
  updatedAt: '2024-01-01T00:00:00.000Z',
};

describe('DynamoDBBookingQueryRepository', () => {
  let repository: DynamoDBBookingQueryRepository;
  let mockSend: jest.Mock;

  beforeEach(() => {
    mockSend = jest.fn();
    (DynamoDBDocumentClient.from as jest.Mock).mockReturnValue({ send: mockSend });
    const mockClient = {} as DynamoDBClient;
    repository = new DynamoDBBookingQueryRepository(mockClient, 'TestBookings');
  });

  describe('findById', () => {
    it('should return booking when found', async () => {
      mockSend.mockResolvedValue({ Item: sampleItem });

      const result = await repository.findById(BookingId.from('booking-1'));

      expect(result).toBeInstanceOf(Booking);
      expect(result!.getId().getValue()).toBe('booking-1');
    });

    it('should return null when not found', async () => {
      mockSend.mockResolvedValue({ Item: undefined });

      const result = await repository.findById(BookingId.from('non-existent'));

      expect(result).toBeNull();
    });
  });

  describe('findByUserId', () => {
    it('should return bookings for user', async () => {
      mockSend.mockResolvedValue({ Items: [sampleItem] });

      const result = await repository.findByUserId(UserId.from('user-123'));

      expect(result).toHaveLength(1);
      expect(result[0].getUserId().getValue()).toBe('user-123');
    });

    it('should return empty array when no items', async () => {
      mockSend.mockResolvedValue({ Items: [] });

      const result = await repository.findByUserId(UserId.from('user-none'));

      expect(result).toEqual([]);
    });

    it('should return empty array when Items is undefined', async () => {
      mockSend.mockResolvedValue({});

      const result = await repository.findByUserId(UserId.from('user-none'));

      expect(result).toEqual([]);
    });
  });

  describe('findByEventId', () => {
    it('should return bookings for event', async () => {
      mockSend.mockResolvedValue({ Items: [sampleItem] });

      const result = await repository.findByEventId(EventId.from('event-456'));

      expect(result).toHaveLength(1);
    });

    it('should return empty array when no items', async () => {
      mockSend.mockResolvedValue({ Items: [] });

      const result = await repository.findByEventId(EventId.from('event-none'));

      expect(result).toEqual([]);
    });

    it('should return empty array when Items is undefined', async () => {
      mockSend.mockResolvedValue({});

      const result = await repository.findByEventId(EventId.from('event-none'));

      expect(result).toEqual([]);
    });
  });

  describe('findAll', () => {
    it('should return bookings with pagination', async () => {
      mockSend.mockResolvedValue({
        Items: [sampleItem],
        LastEvaluatedKey: { PK: 'BOOKING#booking-1', SK: 'BOOKING#booking-1' },
      });

      const result = await repository.findAll(10);

      expect(result.bookings).toHaveLength(1);
      expect(result.lastKey).toBeDefined();
    });

    it('should return empty bookings when no items', async () => {
      mockSend.mockResolvedValue({ Items: undefined });

      const result = await repository.findAll();

      expect(result.bookings).toEqual([]);
      expect(result.lastKey).toBeUndefined();
    });

    it('should pass lastKey for pagination', async () => {
      mockSend.mockResolvedValue({ Items: [] });

      const lastKey = JSON.stringify({ PK: 'BOOKING#x', SK: 'BOOKING#x' });
      await repository.findAll(20, lastKey);

      expect(mockSend).toHaveBeenCalledTimes(1);
    });
  });
});
