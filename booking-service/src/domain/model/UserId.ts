/**
 * UserId - Identificador del usuario que hace la reserva.
 * 
 * ¿Qué es?
 * - Es el ID del usuario (vendría de un servicio de autenticación)
 * - Por ahora lo manejamos como string simple
 * 
 * ¿Por qué un Value Object?
 * - En el futuro podríamos agregar validaciones
 * - Hace el código más expresivo
 * - Separa conceptos: UserId vs EventId vs BookingId
 * 
 * Analogía:
 * - Es como tu número de cliente en una tienda
 * - Te identifica como comprador
 */
export class UserId {
  private constructor(private readonly value: string) {
    if (!value || value.trim().length === 0) {
      throw new Error('UserId cannot be empty');
    }
  }

  static from(value: string): UserId {
    return new UserId(value);
  }

  getValue(): string {
    return this.value;
  }

  equals(other: UserId): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}
