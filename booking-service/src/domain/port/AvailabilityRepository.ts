import { EventAvailability } from '../model/EventAvailability';

export interface AvailabilityRepository {
  save(availability: EventAvailability): Promise<void>;
  findByEventId(eventId: string): Promise<EventAvailability | null>;
  delete(eventId: string): Promise<void>;
}
