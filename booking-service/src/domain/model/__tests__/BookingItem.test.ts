import { BookingItem } from '../BookingItem';
import { TicketType } from '../TicketType';
import { TicketQuantity } from '../TicketQuantity';

describe('BookingItem Entity', () => {
  describe('create', () => {
    it('should create a booking item with valid data', () => {
      const quantity = TicketQuantity.from(2);
      const item = BookingItem.create(TicketType.VIP, quantity, 100);

      expect(item.getId()).toBeDefined();
      expect(item.getTicketType()).toBe(TicketType.VIP);
      expect(item.getQuantity().getValue()).toBe(2);
      expect(item.getUnitPrice()).toBe(100);
    });

    it('should calculate subtotal correctly', () => {
      const quantity = TicketQuantity.from(3);
      const item = BookingItem.create(TicketType.GENERAL, quantity, 50);

      expect(item.getSubtotal()).toBe(150);
    });

    it('should calculate subtotal for single ticket', () => {
      const quantity = TicketQuantity.from(1);
      const item = BookingItem.create(TicketType.EARLY_BIRD, quantity, 75);

      expect(item.getSubtotal()).toBe(75);
    });

    it('should allow zero unit price', () => {
      const quantity = TicketQuantity.from(1);
      const item = BookingItem.create(TicketType.GENERAL, quantity, 0);

      expect(item.getUnitPrice()).toBe(0);
      expect(item.getSubtotal()).toBe(0);
    });

    it('should throw error for negative unit price', () => {
      const quantity = TicketQuantity.from(2);

      expect(() => BookingItem.create(TicketType.VIP, quantity, -10)).toThrow(
        'Unit price must be greater than or equal to 0'
      );
    });

    it('should generate unique ids', () => {
      const quantity = TicketQuantity.from(1);
      const item1 = BookingItem.create(TicketType.VIP, quantity, 100);
      const item2 = BookingItem.create(TicketType.VIP, quantity, 100);

      expect(item1.getId()).not.toBe(item2.getId());
    });
  });

  describe('reconstruct', () => {
    it('should reconstruct a booking item from persistence', () => {
      const id = 'existing-id-123';
      const quantity = TicketQuantity.from(2);

      const item = BookingItem.reconstruct(id, TicketType.VIP, quantity, 100, 200);

      expect(item.getId()).toBe(id);
      expect(item.getTicketType()).toBe(TicketType.VIP);
      expect(item.getQuantity().getValue()).toBe(2);
      expect(item.getUnitPrice()).toBe(100);
      expect(item.getSubtotal()).toBe(200);
    });
  });

  describe('equals', () => {
    it('should return true for items with the same id', () => {
      const quantity = TicketQuantity.from(2);
      const item1 = BookingItem.reconstruct('same-id', TicketType.VIP, quantity, 100, 200);
      const item2 = BookingItem.reconstruct('same-id', TicketType.GENERAL, quantity, 50, 100);

      expect(item1.equals(item2)).toBe(true);
    });

    it('should return false for items with different ids', () => {
      const quantity = TicketQuantity.from(2);
      const item1 = BookingItem.reconstruct('id-1', TicketType.VIP, quantity, 100, 200);
      const item2 = BookingItem.reconstruct('id-2', TicketType.VIP, quantity, 100, 200);

      expect(item1.equals(item2)).toBe(false);
    });
  });

  describe('toString', () => {
    it('should format correctly', () => {
      const quantity = TicketQuantity.from(2);
      const item = BookingItem.create(TicketType.VIP, quantity, 100);

      expect(item.toString()).toBe('2x VIP @ $100 = $200');
    });
  });
});
