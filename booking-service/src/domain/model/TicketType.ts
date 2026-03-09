/**
 * TicketType - Tipo de ticket para un evento.
 *
 * ¿Qué es?
 * - Representa las categorías de tickets disponibles
 * - Solo puede tener 3 valores posibles
 *
 * Categorías:
 * - VIP: Acceso premium con beneficios exclusivos
 * - GENERAL: Entrada estándar al evento
 * - EARLY_BIRD: Precio especial por compra anticipada
 *
 * Analogía:
 * - Es como las clases en un vuelo:
 *   - VIP = "Primera clase"
 *   - GENERAL = "Clase turista"
 *   - EARLY_BIRD = "Tarifa anticipada con descuento"
 */
export enum TicketType {
  VIP = 'VIP',
  GENERAL = 'GENERAL',
  EARLY_BIRD = 'EARLY_BIRD'
}

/**
 * Helper para obtener información y validar tipos de ticket
 */
export class TicketTypeInfo {
  private static readonly displayNames: Record<TicketType, string> = {
    [TicketType.VIP]: 'VIP',
    [TicketType.GENERAL]: 'General Admission',
    [TicketType.EARLY_BIRD]: 'Early Bird'
  };

  /**
   * Retorna el nombre legible del tipo de ticket
   */
  static getDisplayName(type: TicketType): string {
    return this.displayNames[type];
  }

  /**
   * Verifica si un string es un tipo de ticket válido
   */
  static isValid(value: string): boolean {
    return Object.values(TicketType).includes(value as TicketType);
  }

  /**
   * Convierte un string a TicketType con validación
   */
  static fromString(value: string): TicketType {
    if (!this.isValid(value)) {
      throw new Error(
        `Invalid ticket type: ${value}. ` +
        `Valid types are: ${Object.values(TicketType).join(', ')}`
      );
    }
    return value as TicketType;
  }
}
