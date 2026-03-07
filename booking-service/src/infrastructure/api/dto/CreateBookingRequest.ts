import { z } from 'zod';

/**
 * CreateBookingRequest DTO
 * 
 * Why DTOs?
 * - Separate API layer from Domain layer
 * - Validate incoming HTTP requests
 * - API can change without affecting domain
 */

export const CreateBookingRequestSchema = z.object({
  userId: z.string().uuid('userId must be a valid UUID'),
  eventId: z.string().uuid('eventId must be a valid UUID'),
  ticketQuantity: z.number().int().min(1).max(10),
  pricePerTicket: z.number().positive(),
});

export type CreateBookingRequest = z.infer<typeof CreateBookingRequestSchema>;
