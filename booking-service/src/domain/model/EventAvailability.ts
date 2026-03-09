export class EventAvailability {
  constructor(
    public readonly eventId: string,
    public readonly eventName: string,
    public readonly totalCapacity: number,
    public availableTickets: number,
    public readonly eventDate: string,
    public active: boolean = true
  ) {}

  static create(eventId: string, eventName: string, capacity: number, eventDate: string): EventAvailability {
    return new EventAvailability(eventId, eventName, capacity, capacity, eventDate, true);
  }

  hasCapacity(requested: number): boolean {
    return this.active && this.availableTickets >= requested;
  }

  reserveTickets(quantity: number): void {
    if (!this.hasCapacity(quantity)) {
      throw new Error(`Not enough tickets. Available: ${this.availableTickets}, Requested: ${quantity}`);
    }
    this.availableTickets -= quantity;
  }

  deactivate(): void {
    this.active = false;
    this.availableTickets = 0;
  }
}
