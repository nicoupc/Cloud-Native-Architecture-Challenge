/**
 * ReservationTime - Ventana de tiempo para una reserva.
 *
 * ¿Qué es?
 * - Representa el período de tiempo durante el cual una reserva es válida
 * - Tiene un inicio y un fin claramente definidos
 *
 * ¿Por qué un Value Object?
 * - Encapsula la validación (inicio debe ser antes del fin)
 * - Permite comparar y detectar solapamientos entre reservas
 *
 * Analogía:
 * - Es como el horario de una función de cine:
 *   - startTime = "18:00" (inicio de la función)
 *   - endTime = "20:30" (fin de la función)
 *   - No puedes tener una función que termine antes de empezar
 *
 * Reglas de negocio:
 * - startTime debe ser anterior a endTime
 * - Ambas fechas deben ser válidas
 */
export class ReservationTime {
  private constructor(
    private readonly startTime: Date,
    private readonly endTime: Date
  ) {
    this.validate(startTime, endTime);
  }

  static from(startTime: Date, endTime: Date): ReservationTime {
    return new ReservationTime(startTime, endTime);
  }

  private validate(startTime: Date, endTime: Date): void {
    if (!(startTime instanceof Date) || isNaN(startTime.getTime())) {
      throw new Error('Start time must be a valid date');
    }

    if (!(endTime instanceof Date) || isNaN(endTime.getTime())) {
      throw new Error('End time must be a valid date');
    }

    if (startTime >= endTime) {
      throw new Error(
        'Start time must be before end time'
      );
    }
  }

  getStartTime(): Date {
    return this.startTime;
  }

  getEndTime(): Date {
    return this.endTime;
  }

  /**
   * Calcula la duración de la reserva en horas
   */
  getDurationInHours(): number {
    const diffMs = this.endTime.getTime() - this.startTime.getTime();
    return diffMs / (1000 * 60 * 60);
  }

  /**
   * Verifica si la reserva está activa en este momento
   */
  isActive(): boolean {
    const now = new Date();
    return now >= this.startTime && now <= this.endTime;
  }

  /**
   * Verifica si la reserva ha expirado
   */
  hasExpired(): boolean {
    const now = new Date();
    return now > this.endTime;
  }

  /**
   * Verifica si dos reservas se solapan en el tiempo
   */
  overlaps(other: ReservationTime): boolean {
    return this.startTime < other.endTime && this.endTime > other.startTime;
  }

  equals(other: ReservationTime): boolean {
    return (
      this.startTime.getTime() === other.startTime.getTime() &&
      this.endTime.getTime() === other.endTime.getTime()
    );
  }

  toString(): string {
    return `${this.startTime.toISOString()} - ${this.endTime.toISOString()}`;
  }
}
