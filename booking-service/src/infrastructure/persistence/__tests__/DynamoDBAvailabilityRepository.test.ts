import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { DynamoDBAvailabilityRepository } from '../DynamoDBAvailabilityRepository';
import { EventAvailability } from '../../../domain/model/EventAvailability';

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

describe('DynamoDBAvailabilityRepository', () => {
  let repository: DynamoDBAvailabilityRepository;
  let mockSend: jest.Mock;

  beforeEach(() => {
    mockSend = jest.fn();
    (DynamoDBDocumentClient.from as jest.Mock).mockReturnValue({ send: mockSend });
    const mockClient = {} as DynamoDBClient;
    repository = new DynamoDBAvailabilityRepository(mockClient, 'TestEventAvailability');
  });

  describe('save', () => {
    it('should save availability successfully', async () => {
      mockSend.mockResolvedValue({});
      const availability = EventAvailability.create(
        'event-123',
        'Concert',
        500,
        '2024-06-15T20:00:00Z'
      );

      await repository.save(availability);

      expect(mockSend).toHaveBeenCalledTimes(1);
    });
  });

  describe('findByEventId', () => {
    it('should return availability when found', async () => {
      mockSend.mockResolvedValue({
        Item: {
          eventId: 'event-123',
          eventName: 'Concert',
          totalCapacity: 500,
          availableTickets: 450,
          eventDate: '2024-06-15T20:00:00Z',
          active: true,
        },
      });

      const result = await repository.findByEventId('event-123');

      expect(result).toBeInstanceOf(EventAvailability);
      expect(result!.eventId).toBe('event-123');
      expect(result!.eventName).toBe('Concert');
      expect(result!.totalCapacity).toBe(500);
      expect(result!.availableTickets).toBe(450);
      expect(result!.active).toBe(true);
    });

    it('should return null when not found', async () => {
      mockSend.mockResolvedValue({ Item: undefined });

      const result = await repository.findByEventId('non-existent');

      expect(result).toBeNull();
    });
  });

  describe('delete', () => {
    it('should delete availability by eventId', async () => {
      mockSend.mockResolvedValue({});

      await repository.delete('event-123');

      expect(mockSend).toHaveBeenCalledTimes(1);
    });
  });
});
