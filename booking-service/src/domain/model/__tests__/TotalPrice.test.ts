import { TotalPrice } from '../TotalPrice';

describe('TotalPrice Value Object', () => {
  describe('from', () => {
    it('should create valid price', () => {
      const price = TotalPrice.from(150.00);
      expect(price.getAmount()).toBe(150.00);
      expect(price.getCurrency()).toBe('USD');
    });

    it('should create price with custom currency', () => {
      const price = TotalPrice.from(100.00, 'EUR');
      expect(price.getAmount()).toBe(100.00);
      expect(price.getCurrency()).toBe('EUR');
    });

    it('should throw error for negative amount', () => {
      expect(() => TotalPrice.from(-10)).toThrow('cannot be negative');
    });

    it('should throw error for invalid number', () => {
      expect(() => TotalPrice.from(NaN)).toThrow('must be a valid number');
      expect(() => TotalPrice.from(Infinity)).toThrow('must be a valid number');
    });
  });

  describe('calculate', () => {
    it('should calculate total price correctly', () => {
      const price = TotalPrice.calculate(3, 50.00);
      expect(price.getAmount()).toBe(150.00);
    });

    it('should handle decimal prices', () => {
      const price = TotalPrice.calculate(5, 25.50);
      expect(price.getAmount()).toBe(127.50);
    });
  });

  describe('format', () => {
    it('should format price correctly', () => {
      const price = TotalPrice.from(150.00);
      expect(price.format()).toBe('$150.00 USD');
    });

    it('should format with two decimal places', () => {
      const price = TotalPrice.from(99.5);
      expect(price.format()).toBe('$99.50 USD');
    });
  });

  describe('equals', () => {
    it('should return true for equal prices', () => {
      const price1 = TotalPrice.from(100.00);
      const price2 = TotalPrice.from(100.00);

      expect(price1.equals(price2)).toBe(true);
    });

    it('should return false for different amounts', () => {
      const price1 = TotalPrice.from(100.00);
      const price2 = TotalPrice.from(150.00);

      expect(price1.equals(price2)).toBe(false);
    });

    it('should return false for different currencies', () => {
      const price1 = TotalPrice.from(100.00, 'USD');
      const price2 = TotalPrice.from(100.00, 'EUR');

      expect(price1.equals(price2)).toBe(false);
    });
  });
});
