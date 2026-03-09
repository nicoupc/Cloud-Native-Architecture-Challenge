import { AvailabilityRepository } from '../../domain/port/AvailabilityRepository';
import { EventAvailability } from '../../domain/model/EventAvailability';

export interface EventCreatedPayload {
  eventId: string;
  name: string;
  capacity: number;
  eventDate: string;
}

export class UpdateAvailabilityHandler {
  constructor(private readonly availabilityRepository: AvailabilityRepository) {}

  async handle(payload: EventCreatedPayload): Promise<void> {
    const existing = await this.availabilityRepository.findByEventId(payload.eventId);
    if (existing) {
      return; // Idempotent: already processed
    }
    const availability = EventAvailability.create(
      payload.eventId,
      payload.name,
      payload.capacity,
      payload.eventDate
    );
    await this.availabilityRepository.save(availability);
  }
}
