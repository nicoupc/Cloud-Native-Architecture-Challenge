/**
 * TotalPrice - Precio total de una reserva.
 * 
 * ¿Qué es?
 * - Representa el precio total a pagar
 * - Incluye cantidad de tickets × precio por ticket
 * 
 * ¿Por qué un Value Object?
 * - Encapsula validaciones (no puede ser negativo)
 * - Maneja la moneda (por ahora solo USD)
 * - Hace explícito que es un precio, no cualquier número
 * 
 * Analogía:
 * - Es como el total en un recibo de compra
 * - Muestra cuánto debes pagar en total
 * 
 * Reglas de negocio:
 * - Debe ser mayor a 0
 * - Se calcula como: ticketQuantity × pricePerTicket
 */
export class TotalPrice {
  private constructor(
    private readonly amount: number,
    private readonly currency: string = 'USD'
  ) {
    this.validate(amount);
  }

  static from(amount: number, currency: string = 'USD'): TotalPrice {
    return new TotalPrice(amount, currency);
  }

  /**
   * Calcula el precio total basado en cantidad y precio unitario
   * Uso: TotalPrice.calculate(3, 50.00) = $150.00
   */
  static calculate(quantity: number, pricePerTicket: number): TotalPrice {
    const total = quantity * pricePerTicket;
    return new TotalPrice(total);
  }

  private validate(amount: number): void {
    if (amount < 0) {
      throw new Error('Total price cannot be negative');
    }

    if (!Number.isFinite(amount)) {
      throw new Error('Total price must be a valid number');
    }
  }

  getAmount(): number {
    return this.amount;
  }

  getCurrency(): string {
    return this.currency;
  }

  /**
   * Formatea el precio para mostrar
   * Ejemplo: $150.00 USD
   */
  format(): string {
    return `$${this.amount.toFixed(2)} ${this.currency}`;
  }

  equals(other: TotalPrice): boolean {
    return (
      this.amount === other.amount &&
      this.currency === other.currency
    );
  }

  toString(): string {
    return this.format();
  }
}
