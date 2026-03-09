import { TicketType, TicketTypeInfo } from '../TicketType';

describe('TicketType Enum', () => {
  describe('enum values', () => {
    it('should have VIP value', () => {
      expect(TicketType.VIP).toBe('VIP');
    });

    it('should have GENERAL value', () => {
      expect(TicketType.GENERAL).toBe('GENERAL');
    });

    it('should have EARLY_BIRD value', () => {
      expect(TicketType.EARLY_BIRD).toBe('EARLY_BIRD');
    });
  });

  describe('TicketTypeInfo.getDisplayName', () => {
    it('should return display name for VIP', () => {
      expect(TicketTypeInfo.getDisplayName(TicketType.VIP)).toBe('VIP');
    });

    it('should return display name for GENERAL', () => {
      expect(TicketTypeInfo.getDisplayName(TicketType.GENERAL)).toBe('General Admission');
    });

    it('should return display name for EARLY_BIRD', () => {
      expect(TicketTypeInfo.getDisplayName(TicketType.EARLY_BIRD)).toBe('Early Bird');
    });
  });

  describe('TicketTypeInfo.isValid', () => {
    it('should return true for valid ticket types', () => {
      expect(TicketTypeInfo.isValid('VIP')).toBe(true);
      expect(TicketTypeInfo.isValid('GENERAL')).toBe(true);
      expect(TicketTypeInfo.isValid('EARLY_BIRD')).toBe(true);
    });

    it('should return false for invalid ticket types', () => {
      expect(TicketTypeInfo.isValid('INVALID')).toBe(false);
      expect(TicketTypeInfo.isValid('')).toBe(false);
      expect(TicketTypeInfo.isValid('vip')).toBe(false);
    });
  });

  describe('TicketTypeInfo.fromString', () => {
    it('should convert valid string to TicketType', () => {
      expect(TicketTypeInfo.fromString('VIP')).toBe(TicketType.VIP);
      expect(TicketTypeInfo.fromString('GENERAL')).toBe(TicketType.GENERAL);
      expect(TicketTypeInfo.fromString('EARLY_BIRD')).toBe(TicketType.EARLY_BIRD);
    });

    it('should throw error for invalid string', () => {
      expect(() => TicketTypeInfo.fromString('INVALID')).toThrow('Invalid ticket type');
      expect(() => TicketTypeInfo.fromString('')).toThrow('Invalid ticket type');
    });
  });
});
