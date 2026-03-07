/**
 * BookingStatus - Estado de una reserva.
 * 
 * ¿Qué es?
 * - Representa el ciclo de vida de una reserva
 * - Solo puede tener 3 valores posibles
 * 
 * Estados:
 * - PENDING: Reserva creada, esperando confirmación de pago
 * - CONFIRMED: Pago exitoso, reserva confirmada
 * - CANCELLED: Reserva cancelada (por usuario o por fallo de pago)
 * 
 * Analogía:
 * - Es como el estado de un pedido en línea:
 *   - PENDING = "Procesando pago"
 *   - CONFIRMED = "Pedido confirmado"
 *   - CANCELLED = "Pedido cancelado"
 * 
 * Transiciones válidas:
 * - PENDING → CONFIRMED (pago exitoso)
 * - PENDING → CANCELLED (pago fallido o cancelación)
 * - CONFIRMED → CANCELLED (cancelación después de confirmar)
 * 
 * Transiciones inválidas:
 * - CANCELLED → CONFIRMED (no puedes confirmar algo cancelado)
 * - CANCELLED → PENDING (no puedes volver a pending)
 */
export enum BookingStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  CANCELLED = 'CANCELLED'
}

/**
 * Helper para validar transiciones de estado
 */
export class BookingStatusTransition {
  /**
   * Verifica si una transición de estado es válida
   */
  static isValidTransition(from: BookingStatus, to: BookingStatus): boolean {
    // Mapa de transiciones válidas
    const validTransitions: Record<BookingStatus, BookingStatus[]> = {
      [BookingStatus.PENDING]: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
      [BookingStatus.CONFIRMED]: [BookingStatus.CANCELLED],
      [BookingStatus.CANCELLED]: [] // No se puede salir de CANCELLED
    };

    return validTransitions[from].includes(to);
  }

  /**
   * Lanza error si la transición no es válida
   */
  static validateTransition(from: BookingStatus, to: BookingStatus): void {
    if (!this.isValidTransition(from, to)) {
      throw new Error(
        `Invalid status transition: ${from} → ${to}. ` +
        `Cannot transition from ${from} to ${to}.`
      );
    }
  }
}
