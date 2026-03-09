import { BookingController } from '../BookingController';
import { CreateBookingHandler } from '../../../application/command/CreateBookingHandler';
import { ConfirmBookingHandler } from '../../../application/command/ConfirmBookingHandler';
import { CancelBookingHandler } from '../../../application/command/CancelBookingHandler';
import { GetBookingByIdHandler } from '../../../application/query/GetBookingByIdHandler';
import { GetBookingsByUserHandler } from '../../../application/query/GetBookingsByUserHandler';
import { GetBookingsByEventHandler } from '../../../application/query/GetBookingsByEventHandler';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';
import { BookingNotFoundException } from '../../../domain/exception/BookingNotFoundException';
import { InvalidBookingStateException } from '../../../domain/exception/InvalidBookingStateException';
import { BookingId } from '../../../domain/model/BookingId';
import { BookingStatus } from '../../../domain/model/BookingStatus';
import { Request, Response, NextFunction } from 'express';

function createMockReqRes(overrides: { params?: Record<string, string>; body?: Record<string, unknown> } = {}) {
  const req = {
    params: overrides.params || {},
    body: overrides.body || {},
  } as unknown as Request;

  const res = {
    status: jest.fn().mockReturnThis(),
    json: jest.fn().mockReturnThis(),
  } as unknown as Response;

  const next: NextFunction = jest.fn();

  return { req, res, next };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function findRoute(router: any, path: string, method: string) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return router.stack.find((layer: any) =>
    layer.route?.path === path && layer.route?.methods[method]
  );
}

describe('BookingController', () => {
  let controller: BookingController;
  let mockCreateHandler: jest.Mocked<CreateBookingHandler>;
  let mockConfirmHandler: jest.Mocked<ConfirmBookingHandler>;
  let mockCancelHandler: jest.Mocked<CancelBookingHandler>;
  let mockGetByIdHandler: jest.Mocked<GetBookingByIdHandler>;
  let mockGetByUserHandler: jest.Mocked<GetBookingsByUserHandler>;
  let mockGetByEventHandler: jest.Mocked<GetBookingsByEventHandler>;

  const sampleBooking = Booking.create(
    UserId.from('user-123'),
    EventId.from('event-456'),
    TicketQuantity.from(2),
    50.00
  );

  beforeEach(() => {
    mockCreateHandler = { handle: jest.fn() } as unknown as jest.Mocked<CreateBookingHandler>;
    mockConfirmHandler = { handle: jest.fn() } as unknown as jest.Mocked<ConfirmBookingHandler>;
    mockCancelHandler = { handle: jest.fn() } as unknown as jest.Mocked<CancelBookingHandler>;
    mockGetByIdHandler = { handle: jest.fn() } as unknown as jest.Mocked<GetBookingByIdHandler>;
    mockGetByUserHandler = { handle: jest.fn() } as unknown as jest.Mocked<GetBookingsByUserHandler>;
    mockGetByEventHandler = { handle: jest.fn() } as unknown as jest.Mocked<GetBookingsByEventHandler>;

    controller = new BookingController(
      mockCreateHandler,
      mockConfirmHandler,
      mockCancelHandler,
      mockGetByIdHandler,
      mockGetByUserHandler,
      mockGetByEventHandler
    );
  });

  it('should return a router', () => {
    expect(controller.getRouter()).toBeDefined();
  });

  describe('createBooking', () => {
    it('should create booking and return 201', async () => {
      const { req, res, next } = createMockReqRes({
        body: {
          userId: '550e8400-e29b-41d4-a716-446655440000',
          eventId: '550e8400-e29b-41d4-a716-446655440001',
          ticketQuantity: 2,
          pricePerTicket: 50.00,
        },
      });

      mockCreateHandler.handle.mockResolvedValue(sampleBooking);

      const route = findRoute(controller.getRouter(), '/bookings', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({ success: true })
      );
    });

    it('should return 400 for invalid request body', async () => {
      const { req, res, next } = createMockReqRes({
        body: { userId: 'not-a-uuid' },
      });

      const route = findRoute(controller.getRouter(), '/bookings', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(400);
    });
  });

  describe('confirmBooking', () => {
    it('should confirm booking and return 200', async () => {
      const { req, res, next } = createMockReqRes({ params: { id: 'booking-1' } });

      mockConfirmHandler.handle.mockResolvedValue(sampleBooking);

      const route = findRoute(controller.getRouter(), '/bookings/:id/confirm', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({ success: true })
      );
    });

    it('should return 404 when booking not found', async () => {
      const { req, res, next } = createMockReqRes({ params: { id: 'non-existent' } });

      mockConfirmHandler.handle.mockRejectedValue(
        new BookingNotFoundException(BookingId.from('non-existent'))
      );

      const route = findRoute(controller.getRouter(), '/bookings/:id/confirm', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(404);
    });
  });

  describe('cancelBooking', () => {
    it('should cancel booking and return 200', async () => {
      const { req, res, next } = createMockReqRes({
        params: { id: 'booking-1' },
        body: { reason: 'Changed plans' },
      });

      mockCancelHandler.handle.mockResolvedValue(sampleBooking);

      const route = findRoute(controller.getRouter(), '/bookings/:id/cancel', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(200);
    });

    it('should use default reason when not provided', async () => {
      const { req, res, next } = createMockReqRes({
        params: { id: 'booking-1' },
        body: {},
      });

      mockCancelHandler.handle.mockResolvedValue(sampleBooking);

      const route = findRoute(controller.getRouter(), '/bookings/:id/cancel', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(mockCancelHandler.handle).toHaveBeenCalledWith(
        expect.objectContaining({ reason: 'Cancelled by user' })
      );
    });

    it('should return 400 for InvalidBookingStateException', async () => {
      const { req, res, next } = createMockReqRes({
        params: { id: 'booking-1' },
        body: { reason: 'test' },
      });

      mockCancelHandler.handle.mockRejectedValue(
        new InvalidBookingStateException(BookingStatus.CANCELLED, BookingStatus.CANCELLED)
      );

      const route = findRoute(controller.getRouter(), '/bookings/:id/cancel', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(400);
    });
  });

  describe('getBookingById', () => {
    it('should return booking by id', async () => {
      const { req, res, next } = createMockReqRes({ params: { id: 'booking-1' } });

      mockGetByIdHandler.handle.mockResolvedValue(sampleBooking);

      const route = findRoute(controller.getRouter(), '/bookings/:id', 'get');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(200);
    });
  });

  describe('getBookingsByUser', () => {
    it('should return bookings for user', async () => {
      const { req, res, next } = createMockReqRes({ params: { userId: 'user-123' } });

      mockGetByUserHandler.handle.mockResolvedValue([sampleBooking]);

      const route = findRoute(controller.getRouter(), '/bookings/user/:userId', 'get');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({ count: 1 })
      );
    });
  });

  describe('getBookingsByEvent', () => {
    it('should return bookings for event', async () => {
      const { req, res, next } = createMockReqRes({ params: { eventId: 'event-456' } });

      mockGetByEventHandler.handle.mockResolvedValue([sampleBooking]);

      const route = findRoute(controller.getRouter(), '/bookings/event/:eventId', 'get');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({ count: 1 })
      );
    });
  });

  describe('handleError', () => {
    it('should return 500 for unknown errors', async () => {
      const { req, res, next } = createMockReqRes({ params: { id: 'booking-1' } });

      mockConfirmHandler.handle.mockRejectedValue(new Error('Something broke'));

      const route = findRoute(controller.getRouter(), '/bookings/:id/confirm', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(500);
    });

    it('should handle non-Error thrown values', async () => {
      const { req, res, next } = createMockReqRes({ params: { id: 'booking-1' } });

      mockConfirmHandler.handle.mockRejectedValue('string error');

      const route = findRoute(controller.getRouter(), '/bookings/:id/confirm', 'post');
      await route!.route!.stack[0].handle(req, res, next);

      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({ message: 'Unknown error' })
      );
    });
  });
});
