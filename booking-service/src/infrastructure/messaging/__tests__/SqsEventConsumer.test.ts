import { SQSClient } from '@aws-sdk/client-sqs';
import { SqsEventConsumer } from '../SqsEventConsumer';
import { UpdateAvailabilityHandler } from '../../../application/command/UpdateAvailabilityHandler';
import { CancelEventBookingsHandler } from '../../../application/command/CancelEventBookingsHandler';

jest.mock('@aws-sdk/client-sqs', () => {
  const actual = jest.requireActual('@aws-sdk/client-sqs');
  return {
    ...actual,
    SQSClient: jest.fn(),
    ReceiveMessageCommand: jest.fn(),
    DeleteMessageCommand: jest.fn(),
  };
});

describe('SqsEventConsumer', () => {
  let consumer: SqsEventConsumer;
  let mockSend: jest.Mock;
  let mockUpdateHandler: jest.Mocked<UpdateAvailabilityHandler>;
  let mockCancelHandler: jest.Mocked<CancelEventBookingsHandler>;

  beforeEach(() => {
    mockSend = jest.fn();
    const mockClient = { send: mockSend } as unknown as SQSClient;

    mockUpdateHandler = {
      handle: jest.fn(),
    } as any;

    mockCancelHandler = {
      handle: jest.fn(),
    } as any;

    consumer = new SqsEventConsumer(
      mockClient,
      'http://localhost:4566/000000000000/booking-events-queue',
      mockUpdateHandler,
      mockCancelHandler
    );
  });

  it('should dispatch EventCreated to UpdateAvailabilityHandler', async () => {
    const message = {
      MessageId: 'msg-1',
      ReceiptHandle: 'receipt-1',
      Body: JSON.stringify({
        'detail-type': 'EventCreated',
        detail: {
          eventId: 'event-123',
          name: 'Concert',
          capacity: 500,
          eventDate: '2024-06-15T20:00:00Z',
        },
      }),
    };

    // First call returns messages, second call returns nothing (to stop loop)
    mockSend
      .mockResolvedValueOnce({ Messages: [message] })
      .mockResolvedValueOnce({}); // DeleteMessage response

    mockUpdateHandler.handle.mockResolvedValue();

    // Access private method via any
    await (consumer as any).pollMessages();

    expect(mockUpdateHandler.handle).toHaveBeenCalledWith({
      eventId: 'event-123',
      name: 'Concert',
      capacity: 500,
      eventDate: '2024-06-15T20:00:00Z',
    });
    // Should delete message after successful processing
    expect(mockSend).toHaveBeenCalledTimes(2);
  });

  it('should dispatch EventCancelled to CancelEventBookingsHandler', async () => {
    const message = {
      MessageId: 'msg-2',
      ReceiptHandle: 'receipt-2',
      Body: JSON.stringify({
        'detail-type': 'EventCancelled',
        detail: {
          eventId: 'event-456',
          reason: 'Weather conditions',
        },
      }),
    };

    mockSend
      .mockResolvedValueOnce({ Messages: [message] })
      .mockResolvedValueOnce({}); // DeleteMessage response

    mockCancelHandler.handle.mockResolvedValue(3);

    await (consumer as any).pollMessages();

    expect(mockCancelHandler.handle).toHaveBeenCalledWith({
      eventId: 'event-456',
      reason: 'Weather conditions',
    });
    expect(mockSend).toHaveBeenCalledTimes(2);
  });

  it('should skip unknown event types', async () => {
    const message = {
      MessageId: 'msg-3',
      ReceiptHandle: 'receipt-3',
      Body: JSON.stringify({
        'detail-type': 'UnknownEvent',
        detail: { foo: 'bar' },
      }),
    };

    mockSend
      .mockResolvedValueOnce({ Messages: [message] })
      .mockResolvedValueOnce({}); // DeleteMessage response

    await (consumer as any).pollMessages();

    expect(mockUpdateHandler.handle).not.toHaveBeenCalled();
    expect(mockCancelHandler.handle).not.toHaveBeenCalled();
    // Should still delete the message
    expect(mockSend).toHaveBeenCalledTimes(2);
  });

  it('should handle empty response (no messages)', async () => {
    mockSend.mockResolvedValueOnce({ Messages: [] });

    await (consumer as any).pollMessages();

    expect(mockUpdateHandler.handle).not.toHaveBeenCalled();
    expect(mockCancelHandler.handle).not.toHaveBeenCalled();
    expect(mockSend).toHaveBeenCalledTimes(1);
  });

  it('should not delete message if processing fails', async () => {
    const message = {
      MessageId: 'msg-4',
      ReceiptHandle: 'receipt-4',
      Body: JSON.stringify({
        'detail-type': 'EventCreated',
        detail: {
          eventId: 'event-789',
          name: 'Failed Event',
          capacity: 100,
          eventDate: '2024-08-01T10:00:00Z',
        },
      }),
    };

    mockSend.mockResolvedValueOnce({ Messages: [message] });
    mockUpdateHandler.handle.mockRejectedValue(new Error('DB Error'));

    await (consumer as any).pollMessages();

    // Only one send call (ReceiveMessage), no DeleteMessage
    expect(mockSend).toHaveBeenCalledTimes(1);
  });

  it('should stop polling when stop() is called', () => {
    consumer.stop();
    expect((consumer as any).running).toBe(false);
  });
});
