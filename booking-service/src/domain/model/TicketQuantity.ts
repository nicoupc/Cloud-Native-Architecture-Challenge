/**
 * TicketQuantity - Cantidad de tickets en una reserva.
 * 
 * ¿Qué es?
 * - Representa cuántos tickets se están reservando
 * - Debe ser un número positivo
 * 
 * ¿Por qué un Value Object?
 * - Encapsula la validación (no puede ser 0 o negativo)
 * - Hace explícito que es una cantidad de tickets, no cualquier número
 * 
 * Analogía:
 * - Es como decir "quiero 3 entradas para el cine"
 * - No puedes pedir 0 entradas o -5 entradas
 * 
 * Reglas de negocio:
 * - Mínimo: 1 ticket
 * - Máximo: 10 tickets por reserva (límite de negocio)
 */
export class TicketQuantity {
  private static readonly MIN_QUANTITY = 1;
  private static readonly MAX_QUANTITY = 10;

  private constructor(private readonly value: number) {
    this.validate(value);
  }

  static from(value: number): TicketQuantity {
    return new TicketQuantity(value);
  }

  private validate(value: number): void {
    if (!Number.isInteger(value)) {
      throw new Error('Ticket quantity must be an integer');
    }

    if (value < TicketQuantity.MIN_QUANTITY) {
      throw new Error(
        `Ticket quantity must be at least ${TicketQuantity.MIN_QUANTITY}`
      );
    }

    if (value > TicketQuantity.MAX_QUANTITY) {
      throw new Error(
        `Ticket quantity cannot exceed ${TicketQuantity.MAX_QUANTITY} per booking`
      );
    }
  }

  getValue(): number {
    return this.value;
  }

  /**
   * Suma dos cantidades de tickets
   * Útil para calcular totales
   */
  add(other: TicketQuantity): TicketQuantity {
    return TicketQuantity.from(this.value + other.value);
  }

  equals(other: TicketQuantity): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return `${this.value} ticket(s)`;
  }
}
