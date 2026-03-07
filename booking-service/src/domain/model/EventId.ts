/**
 * EventId - Identificador del evento para el cual se hace la reserva.
 * 
 * ¿Qué es?
 * - Es el ID del evento (viene del Event Service)
 * - Conecta la reserva con un evento específico
 * 
 * ¿Por qué un Value Object?
 * - Hace explícita la relación entre Booking y Event
 * - Evita confundir IDs de diferentes entidades
 * 
 * Analogía:
 * - Es como el número de función en un cine
 * - Identifica para qué película es tu ticket
 */
export class EventId {
  private constructor(private readonly value: string) {
    if (!value || value.trim().length === 0) {
      throw new Error('EventId cannot be empty');
    }
  }

  static from(value: string): EventId {
    return new EventId(value);
  }

  getValue(): string {
    return this.value;
  }

  equals(other: EventId): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}
