import { CreateBookingRequestSchema } from '../CreateBookingRequest';

describe('CreateBookingRequestSchema', () => {
  it('should validate a correct request', () => {
    const input = {
      userId: '550e8400-e29b-41d4-a716-446655440000',
      eventId: '550e8400-e29b-41d4-a716-446655440001',
      ticketQuantity: 3,
      pricePerTicket: 50.00,
    };

    const result = CreateBookingRequestSchema.safeParse(input);
    expect(result.success).toBe(true);
  });

  it('should reject invalid userId', () => {
    const input = {
      userId: 'not-a-uuid',
      eventId: '550e8400-e29b-41d4-a716-446655440001',
      ticketQuantity: 3,
      pricePerTicket: 50.00,
    };

    const result = CreateBookingRequestSchema.safeParse(input);
    expect(result.success).toBe(false);
  });

  it('should reject ticket quantity less than 1', () => {
    const input = {
      userId: '550e8400-e29b-41d4-a716-446655440000',
      eventId: '550e8400-e29b-41d4-a716-446655440001',
      ticketQuantity: 0,
      pricePerTicket: 50.00,
    };

    const result = CreateBookingRequestSchema.safeParse(input);
    expect(result.success).toBe(false);
  });

  it('should reject ticket quantity greater than 10', () => {
    const input = {
      userId: '550e8400-e29b-41d4-a716-446655440000',
      eventId: '550e8400-e29b-41d4-a716-446655440001',
      ticketQuantity: 11,
      pricePerTicket: 50.00,
    };

    const result = CreateBookingRequestSchema.safeParse(input);
    expect(result.success).toBe(false);
  });

  it('should reject negative price', () => {
    const input = {
      userId: '550e8400-e29b-41d4-a716-446655440000',
      eventId: '550e8400-e29b-41d4-a716-446655440001',
      ticketQuantity: 2,
      pricePerTicket: -10,
    };

    const result = CreateBookingRequestSchema.safeParse(input);
    expect(result.success).toBe(false);
  });
});
