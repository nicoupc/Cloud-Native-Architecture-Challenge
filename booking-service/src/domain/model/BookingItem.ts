/**
 * BookingItem - Línea de detalle dentro de una reserva.
 *
 * ¿Qué es?
 * - Representa un ítem individual dentro del agregado Booking
 * - Contiene el tipo de ticket, cantidad, precio unitario y subtotal
 *
 * ¿Por qué una Entidad?
 * - Tiene identidad propia (id único)
 * - Puede ser referenciado individualmente dentro de la reserva
 *
 * Analogía:
 * - Es como una línea en un recibo de compra:
 *   - "2x VIP @ $100 = $200"
 *   - Cada línea tiene su propio detalle y subtotal
 *
 * Reglas de negocio:
 * - El precio unitario no puede ser negativo
 * - El subtotal se calcula automáticamente (cantidad × precio unitario)
 */
import { v4 as uuidv4 } from 'uuid';
import { TicketType } from './TicketType';
import { TicketQuantity } from './TicketQuantity';

export class BookingItem {
  private constructor(
    private readonly id: string,
    private readonly ticketType: TicketType,
    private readonly quantity: TicketQuantity,
    private readonly unitPrice: number,
    private readonly subtotal: number
  ) {}

  /**
   * Crea un nuevo BookingItem con id generado y subtotal calculado
   */
  static create(
    ticketType: TicketType,
    quantity: TicketQuantity,
    unitPrice: number
  ): BookingItem {
    BookingItem.validateUnitPrice(unitPrice);
    const subtotal = quantity.getValue() * unitPrice;
    return new BookingItem(uuidv4(), ticketType, quantity, unitPrice, subtotal);
  }

  /**
   * Reconstruye un BookingItem desde persistencia
   */
  static reconstruct(
    id: string,
    ticketType: TicketType,
    quantity: TicketQuantity,
    unitPrice: number,
    subtotal: number
  ): BookingItem {
    return new BookingItem(id, ticketType, quantity, unitPrice, subtotal);
  }

  private static validateUnitPrice(unitPrice: number): void {
    if (unitPrice < 0) {
      throw new Error('Unit price must be greater than or equal to 0');
    }
  }

  getId(): string {
    return this.id;
  }

  getTicketType(): TicketType {
    return this.ticketType;
  }

  getQuantity(): TicketQuantity {
    return this.quantity;
  }

  getUnitPrice(): number {
    return this.unitPrice;
  }

  getSubtotal(): number {
    return this.subtotal;
  }

  /**
   * Compara dos BookingItems por identidad (id)
   */
  equals(other: BookingItem): boolean {
    return this.id === other.id;
  }

  toString(): string {
    return `${this.quantity.getValue()}x ${this.ticketType} @ $${this.unitPrice} = $${this.subtotal}`;
  }
}
