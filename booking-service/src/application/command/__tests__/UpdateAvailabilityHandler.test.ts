import { UpdateAvailabilityHandler, EventCreatedPayload } from '../UpdateAvailabilityHandler';
import { AvailabilityRepository } from '../../../domain/port/AvailabilityRepository';
import { EventAvailability } from '../../../domain/model/EventAvailability';

describe('UpdateAvailabilityHandler', () => {
  let handler: UpdateAvailabilityHandler;
  let mockRepository: jest.Mocked<AvailabilityRepository>;

  beforeEach(() => {
    mockRepository = {
      save: jest.fn(),
      findByEventId: jest.fn(),
      delete: jest.fn(),
    };

    handler = new UpdateAvailabilityHandler(mockRepository);
  });

  it('should create availability for new event', async () => {
    const payload: EventCreatedPayload = {
      eventId: 'event-123',
      name: 'Concert',
      capacity: 500,
      eventDate: '2024-06-15T20:00:00Z',
    };

    mockRepository.findByEventId.mockResolvedValue(null);
    mockRepository.save.mockResolvedValue();

    await handler.handle(payload);

    expect(mockRepository.findByEventId).toHaveBeenCalledWith('event-123');
    expect(mockRepository.save).toHaveBeenCalledTimes(1);
    const savedAvailability = mockRepository.save.mock.calls[0][0];
    expect(savedAvailability).toBeInstanceOf(EventAvailability);
    expect(savedAvailability.eventId).toBe('event-123');
    expect(savedAvailability.eventName).toBe('Concert');
    expect(savedAvailability.totalCapacity).toBe(500);
    expect(savedAvailability.availableTickets).toBe(500);
    expect(savedAvailability.eventDate).toBe('2024-06-15T20:00:00Z');
    expect(savedAvailability.active).toBe(true);
  });

  it('should be idempotent - skip if already exists', async () => {
    const payload: EventCreatedPayload = {
      eventId: 'event-123',
      name: 'Concert',
      capacity: 500,
      eventDate: '2024-06-15T20:00:00Z',
    };

    const existing = EventAvailability.create('event-123', 'Concert', 500, '2024-06-15T20:00:00Z');
    mockRepository.findByEventId.mockResolvedValue(existing);

    await handler.handle(payload);

    expect(mockRepository.findByEventId).toHaveBeenCalledWith('event-123');
    expect(mockRepository.save).not.toHaveBeenCalled();
  });

  it('should handle payload with zero capacity', async () => {
    const payload: EventCreatedPayload = {
      eventId: 'event-456',
      name: 'Free Event',
      capacity: 0,
      eventDate: '2024-07-01T10:00:00Z',
    };

    mockRepository.findByEventId.mockResolvedValue(null);
    mockRepository.save.mockResolvedValue();

    await handler.handle(payload);

    expect(mockRepository.save).toHaveBeenCalledTimes(1);
    const savedAvailability = mockRepository.save.mock.calls[0][0];
    expect(savedAvailability.totalCapacity).toBe(0);
    expect(savedAvailability.availableTickets).toBe(0);
  });
});
