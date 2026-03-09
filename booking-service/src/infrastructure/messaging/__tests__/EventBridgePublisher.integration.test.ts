import * as net from 'net';
import {
  EventBridgeClient,
  CreateEventBusCommand,
  DeleteEventBusCommand,
} from '@aws-sdk/client-eventbridge';
import { EventBridgePublisher } from '../EventBridgePublisher';
import { BookingCreated } from '../../../domain/event/BookingCreated';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';

const LOCALSTACK_ENDPOINT = 'http://localhost:4566';
const TEST_BUS_NAME = 'integration-test-bus';

let skipTests = false;
let eventBridgeClient: EventBridgeClient;
let publisher: EventBridgePublisher;

function checkLocalStack(): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    socket.setTimeout(1000);
    socket.once('connect', () => { socket.destroy(); resolve(true); });
    socket.once('error', () => { socket.destroy(); resolve(false); });
    socket.once('timeout', () => { socket.destroy(); resolve(false); });
    socket.connect(4566, '127.0.0.1');
  });
}

beforeAll(async () => {
  const available = await checkLocalStack();
  if (!available) {
    skipTests = true;
    console.log('⚠️  LocalStack not available, skipping integration tests');
    return;
  }

  eventBridgeClient = new EventBridgeClient({
    endpoint: LOCALSTACK_ENDPOINT,
    region: 'us-east-1',
    credentials: { accessKeyId: 'test', secretAccessKey: 'test' },
  });

  try {
    await eventBridgeClient.send(new CreateEventBusCommand({ Name: TEST_BUS_NAME }));
  } catch (error: any) {
    if (error.name !== 'ResourceAlreadyExistsException') throw error;
  }

  publisher = new EventBridgePublisher(eventBridgeClient, TEST_BUS_NAME, 'booking-service');
}, 15000);

afterAll(async () => {
  if (skipTests) return;
  try {
    await eventBridgeClient.send(new DeleteEventBusCommand({ Name: TEST_BUS_NAME }));
  } catch {
    // ignore cleanup errors
  }
});

describe('EventBridgePublisher Integration Tests', () => {
  it('should publish a BookingCreated event without errors', async () => {
    if (skipTests) return;

    const booking = Booking.create(
      UserId.from('user-pub-1'),
      EventId.from('event-pub-1'),
      TicketQuantity.from(2),
      75.00
    );

    const event = BookingCreated.from(booking);

    await expect(publisher.publish(event)).resolves.not.toThrow();
  }, 15000);

  it('should publish a batch of events without errors', async () => {
    if (skipTests) return;

    const events = [1, 2, 3].map(i => {
      const booking = Booking.create(
        UserId.from(`user-batch-${i}`),
        EventId.from(`event-batch-${i}`),
        TicketQuantity.from(1),
        25.00
      );
      return BookingCreated.from(booking);
    });

    await expect(publisher.publishBatch(events)).resolves.not.toThrow();
  }, 15000);

  it('should handle empty batch gracefully', async () => {
    if (skipTests) return;

    await expect(publisher.publishBatch([])).resolves.not.toThrow();
  }, 15000);
});
