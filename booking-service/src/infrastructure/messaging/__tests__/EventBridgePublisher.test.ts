import { EventBridgeClient } from '@aws-sdk/client-eventbridge';
import { EventBridgePublisher } from '../EventBridgePublisher';
import { DomainEvent } from '../../../domain/event/DomainEvent';

jest.mock('@aws-sdk/client-eventbridge', () => {
  const actual = jest.requireActual('@aws-sdk/client-eventbridge');
  return {
    ...actual,
    EventBridgeClient: jest.fn(),
    PutEventsCommand: jest.fn(),
  };
});

function createMockEvent(overrides: Partial<DomainEvent> = {}): DomainEvent {
  return {
    eventId: 'evt-1',
    aggregateId: 'agg-1',
    eventType: 'TestEvent',
    occurredAt: new Date('2024-01-01'),
    ...overrides,
  };
}

describe('EventBridgePublisher', () => {
  let publisher: EventBridgePublisher;
  let mockSend: jest.Mock;

  beforeEach(() => {
    mockSend = jest.fn();
    const mockClient = { send: mockSend } as unknown as EventBridgeClient;
    publisher = new EventBridgePublisher(mockClient, 'test-bus', 'test-source');
  });

  describe('publish', () => {
    it('should publish single event successfully', async () => {
      mockSend.mockResolvedValue({ FailedEntryCount: 0, Entries: [{}] });

      const event = createMockEvent();
      await publisher.publish(event);

      expect(mockSend).toHaveBeenCalledTimes(1);
    });

    it('should throw error when event publish fails', async () => {
      mockSend.mockResolvedValue({
        FailedEntryCount: 1,
        Entries: [{ ErrorMessage: 'Access denied' }],
      });

      const event = createMockEvent();
      await expect(publisher.publish(event)).rejects.toThrow('Failed to publish event: Access denied');
    });

    it('should handle unknown error message', async () => {
      mockSend.mockResolvedValue({
        FailedEntryCount: 1,
        Entries: [{}],
      });

      const event = createMockEvent();
      await expect(publisher.publish(event)).rejects.toThrow('Failed to publish event: Unknown error');
    });
  });

  describe('publishBatch', () => {
    it('should do nothing for empty array', async () => {
      await publisher.publishBatch([]);
      expect(mockSend).not.toHaveBeenCalled();
    });

    it('should publish batch of events', async () => {
      mockSend.mockResolvedValue({ FailedEntryCount: 0 });

      const events = [createMockEvent({ eventId: '1' }), createMockEvent({ eventId: '2' })];
      await publisher.publishBatch(events);

      expect(mockSend).toHaveBeenCalledTimes(1);
    });

    it('should split into chunks of 10', async () => {
      mockSend.mockResolvedValue({ FailedEntryCount: 0 });

      const events = Array.from({ length: 15 }, (_, i) =>
        createMockEvent({ eventId: `evt-${i}` })
      );
      await publisher.publishBatch(events);

      expect(mockSend).toHaveBeenCalledTimes(2);
    });

    it('should throw error when batch publish fails', async () => {
      mockSend.mockResolvedValue({ FailedEntryCount: 2 });

      const events = [createMockEvent()];
      await expect(publisher.publishBatch(events)).rejects.toThrow('Failed to publish 2 events');
    });
  });
});
