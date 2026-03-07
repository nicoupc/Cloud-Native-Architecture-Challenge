import { v4 as uuidv4 } from 'uuid';

/**
 * BookingId - Identificador único de una reserva.
 * 
 * ¿Qué es?
 * - Es como el "DNI" de una reserva
 * - Cada reserva tiene un ID único que nunca cambia
 * 
 * ¿Por qué un Value Object y no solo un string?
 * - Encapsula la lógica de generación de IDs
 * - Valida que el ID sea válido
 * - Hace el código más expresivo: BookingId vs string
 * 
 * Analogía:
 * - Es como un número de orden en un restaurante
 * - Una vez asignado, no cambia
 * - Te identifica de forma única
 */
export class BookingId {
  private constructor(private readonly value: string) {
    if (!value || value.trim().length === 0) {
      throw new Error('BookingId cannot be empty');
    }
  }

  /**
   * Genera un nuevo BookingId aleatorio
   * Uso: const id = BookingId.generate();
   */
  static generate(): BookingId {
    return new BookingId(uuidv4());
  }

  /**
   * Crea un BookingId desde un string existente
   * Uso: const id = BookingId.from('123e4567-e89b-12d3-a456-426614174000');
   */
  static from(value: string): BookingId {
    return new BookingId(value);
  }

  /**
   * Obtiene el valor del ID como string
   */
  getValue(): string {
    return this.value;
  }

  /**
   * Compara si dos BookingIds son iguales
   */
  equals(other: BookingId): boolean {
    return this.value === other.value;
  }

  /**
   * Convierte a string para logs y debugging
   */
  toString(): string {
    return this.value;
  }
}
