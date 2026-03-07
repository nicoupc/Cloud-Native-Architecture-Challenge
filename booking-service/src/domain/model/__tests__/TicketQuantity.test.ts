import { TicketQuantity } from '../TicketQuantity';

describe('TicketQuantity Value Object', () => {
  describe('from', () => {
    it('should create valid ticket quantity', () => {
      const quantity = TicketQuantity.from(5);
      expect(quantity.getValue()).toBe(5);
    });

    it('should throw error for quantity less than 1', () => {
      expect(() => TicketQuantity.from(0)).toThrow('must be at least 1');
      expect(() => TicketQuantity.from(-1)).toThrow('must be at least 1');
    });

    it('should throw error for quantity greater than 10', () => {
      expect(() => TicketQuantity.from(11)).toThrow('cannot exceed 10');
      expect(() => TicketQuantity.from(100)).toThrow('cannot exceed 10');
    });

    it('should throw error for non-integer values', () => {
      expect(() => TicketQuantity.from(2.5)).toThrow('must be an integer');
    });
  });

  describe('add', () => {
    it('should add two quantities correctly', () => {
      const qty1 = TicketQuantity.from(3);
      const qty2 = TicketQuantity.from(2);

      const result = qty1.add(qty2);

      expect(result.getValue()).toBe(5);
    });
  });

  describe('equals', () => {
    it('should return true for equal quantities', () => {
      const qty1 = TicketQuantity.from(5);
      const qty2 = TicketQuantity.from(5);

      expect(qty1.equals(qty2)).toBe(true);
    });

    it('should return false for different quantities', () => {
      const qty1 = TicketQuantity.from(5);
      const qty2 = TicketQuantity.from(3);

      expect(qty1.equals(qty2)).toBe(false);
    });
  });

  describe('toString', () => {
    it('should format correctly for single ticket', () => {
      const quantity = TicketQuantity.from(1);
      expect(quantity.toString()).toBe('1 ticket(s)');
    });

    it('should format correctly for multiple tickets', () => {
      const quantity = TicketQuantity.from(5);
      expect(quantity.toString()).toBe('5 ticket(s)');
    });
  });
});
