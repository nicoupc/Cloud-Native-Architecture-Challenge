import * as net from 'net';
import { DynamoDBClient, CreateTableCommand, DeleteTableCommand, DescribeTableCommand } from '@aws-sdk/client-dynamodb';
import { DynamoDBBookingRepository } from '../DynamoDBBookingRepository';
import { Booking } from '../../../domain/model/Booking';
import { BookingId } from '../../../domain/model/BookingId';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';

const LOCALSTACK_ENDPOINT = 'http://localhost:4566';
const TABLE_NAME = 'Bookings-integration-test';

let skipTests = false;
let dynamoClient: DynamoDBClient;
let repository: DynamoDBBookingRepository;

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

async function waitForTable(client: DynamoDBClient, tableName: string): Promise<void> {
  for (let i = 0; i < 30; i++) {
    try {
      const result = await client.send(new DescribeTableCommand({ TableName: tableName }));
      if (result.Table?.TableStatus === 'ACTIVE') return;
    } catch {
      // table not ready yet
    }
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error(`Table ${tableName} did not become ACTIVE`);
}

beforeAll(async () => {
  const available = await checkLocalStack();
  if (!available) {
    skipTests = true;
    console.log('⚠️  LocalStack not available, skipping integration tests');
    return;
  }

  dynamoClient = new DynamoDBClient({
    endpoint: LOCALSTACK_ENDPOINT,
    region: 'us-east-1',
    credentials: { accessKeyId: 'test', secretAccessKey: 'test' },
  });

  // Delete table if it exists from a previous run
  try {
    await dynamoClient.send(new DeleteTableCommand({ TableName: TABLE_NAME }));
    await new Promise(r => setTimeout(r, 1000));
  } catch {
    // table doesn't exist, that's fine
  }

  // Create table matching init-dynamodb.sh schema
  await dynamoClient.send(new CreateTableCommand({
    TableName: TABLE_NAME,
    AttributeDefinitions: [
      { AttributeName: 'PK', AttributeType: 'S' },
      { AttributeName: 'SK', AttributeType: 'S' },
      { AttributeName: 'userId', AttributeType: 'S' },
      { AttributeName: 'eventId', AttributeType: 'S' },
      { AttributeName: 'createdAt', AttributeType: 'S' },
    ],
    KeySchema: [
      { AttributeName: 'PK', KeyType: 'HASH' },
      { AttributeName: 'SK', KeyType: 'RANGE' },
    ],
    GlobalSecondaryIndexes: [
      {
        IndexName: 'UserBookingsIndex',
        KeySchema: [
          { AttributeName: 'userId', KeyType: 'HASH' },
          { AttributeName: 'createdAt', KeyType: 'RANGE' },
        ],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 },
      },
      {
        IndexName: 'EventBookingsIndex',
        KeySchema: [
          { AttributeName: 'eventId', KeyType: 'HASH' },
          { AttributeName: 'createdAt', KeyType: 'RANGE' },
        ],
        Projection: { ProjectionType: 'ALL' },
        ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 },
      },
    ],
    ProvisionedThroughput: { ReadCapacityUnits: 5, WriteCapacityUnits: 5 },
  }));

  await waitForTable(dynamoClient, TABLE_NAME);
  repository = new DynamoDBBookingRepository(dynamoClient, TABLE_NAME);
}, 30000);

afterAll(async () => {
  if (skipTests) return;
  try {
    await dynamoClient.send(new DeleteTableCommand({ TableName: TABLE_NAME }));
  } catch {
    // ignore cleanup errors
  }
}, 10000);

describe('DynamoDBBookingRepository Integration Tests', () => {
  it('should save and retrieve a booking by ID', async () => {
    if (skipTests) return;

    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );

    await repository.save(booking);

    const found = await repository.findById(booking.getId());

    expect(found).not.toBeNull();
    expect(found!.getId().getValue()).toBe(booking.getId().getValue());
    expect(found!.getUserId().getValue()).toBe('user-123');
    expect(found!.getEventId().getValue()).toBe('event-456');
    expect(found!.getTicketQuantity().getValue()).toBe(2);
    expect(found!.getTotalPrice().getAmount()).toBe(100.00);
    expect(found!.getStatus()).toBe('PENDING');
  }, 15000);

  it('should return null for non-existent booking', async () => {
    if (skipTests) return;

    const nonExistentId = BookingId.generate();
    const found = await repository.findById(nonExistentId);

    expect(found).toBeNull();
  }, 15000);

  it('should delete a booking', async () => {
    if (skipTests) return;

    const booking = Booking.create(
      UserId.from('user-del'),
      EventId.from('event-del'),
      TicketQuantity.from(1),
      25.00
    );

    await repository.save(booking);

    const beforeDelete = await repository.findById(booking.getId());
    expect(beforeDelete).not.toBeNull();

    await repository.delete(booking.getId());

    const afterDelete = await repository.findById(booking.getId());
    expect(afterDelete).toBeNull();
  }, 15000);

  it('should update an existing booking (upsert)', async () => {
    if (skipTests) return;

    const booking = Booking.create(
      UserId.from('user-upd'),
      EventId.from('event-upd'),
      TicketQuantity.from(3),
      30.00
    );

    await repository.save(booking);

    booking.confirm();
    await repository.save(booking);

    const found = await repository.findById(booking.getId());
    expect(found).not.toBeNull();
    expect(found!.getStatus()).toBe('CONFIRMED');
  }, 15000);
});
