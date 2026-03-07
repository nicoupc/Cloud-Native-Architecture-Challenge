import { Router, Request, Response } from 'express';
import { CreateBookingHandler } from '../../application/command/CreateBookingHandler';
import { ConfirmBookingHandler } from '../../application/command/ConfirmBookingHandler';
import { CancelBookingHandler } from '../../application/command/CancelBookingHandler';
import { GetBookingByIdHandler } from '../../application/query/GetBookingByIdHandler';
import { GetBookingsByUserHandler } from '../../application/query/GetBookingsByUserHandler';
import { GetBookingsByEventHandler } from '../../application/query/GetBookingsByEventHandler';
import { CreateBookingCommand } from '../../domain/command/CreateBookingCommand';
import { ConfirmBookingCommand } from '../../domain/command/ConfirmBookingCommand';
import { CancelBookingCommand } from '../../domain/command/CancelBookingCommand';
import { GetBookingByIdQuery } from '../../domain/query/GetBookingByIdQuery';
import { GetBookingsByUserQuery } from '../../domain/query/GetBookingsByUserQuery';
import { GetBookingsByEventQuery } from '../../domain/query/GetBookingsByEventQuery';
import { CreateBookingRequestSchema } from './dto/CreateBookingRequest';
import { BookingResponseMapper } from './dto/BookingResponse';
import { BookingNotFoundException } from '../../domain/exception/BookingNotFoundException';
import { InvalidBookingStateException } from '../../domain/exception/InvalidBookingStateException';

/**
 * BookingController - REST API endpoints
 * 
 * Hexagonal Architecture:
 * - This is an INPUT adapter (Primary/Driving adapter)
 * - Receives HTTP requests
 * - Converts to Commands/Queries
 * - Delegates to Application Layer handlers
 * 
 * CQRS:
 * - POST endpoints → Commands (write operations)
 * - GET endpoints → Queries (read operations)
 */
export class BookingController {
  private router: Router;

  constructor(
    private readonly createBookingHandler: CreateBookingHandler,
    private readonly confirmBookingHandler: ConfirmBookingHandler,
    private readonly cancelBookingHandler: CancelBookingHandler,
    private readonly getBookingByIdHandler: GetBookingByIdHandler,
    private readonly getBookingsByUserHandler: GetBookingsByUserHandler,
    private readonly getBookingsByEventHandler: GetBookingsByEventHandler
  ) {
    this.router = Router();
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // Commands (Write operations)
    this.router.post('/bookings', this.createBooking.bind(this));
    this.router.post('/bookings/:id/confirm', this.confirmBooking.bind(this));
    this.router.post('/bookings/:id/cancel', this.cancelBooking.bind(this));

    // Queries (Read operations) - specific routes BEFORE generic :id
    this.router.get('/bookings/user/:userId', this.getBookingsByUser.bind(this));
    this.router.get('/bookings/event/:eventId', this.getBookingsByEvent.bind(this));
    this.router.get('/bookings/:id', this.getBookingById.bind(this));
  }

  /**
   * POST /api/v1/bookings
   * Creates a new booking
   */
  private async createBooking(req: Request, res: Response): Promise<void> {
    try {
      // Validate request body
      const validatedData = CreateBookingRequestSchema.parse(req.body);

      // Create command
      const command = new CreateBookingCommand(
        validatedData.userId,
        validatedData.eventId,
        validatedData.ticketQuantity,
        validatedData.pricePerTicket
      );

      // Execute command
      const booking = await this.createBookingHandler.handle(command);

      // Return response
      res.status(201).json({
        success: true,
        data: BookingResponseMapper.fromDomain(booking),
      });
    } catch (error) {
      this.handleError(error, res);
    }
  }

  /**
   * POST /api/v1/bookings/:id/confirm
   * Confirms a booking after payment
   */
  private async confirmBooking(req: Request, res: Response): Promise<void> {
    try {
      const command = new ConfirmBookingCommand(req.params.id);
      const booking = await this.confirmBookingHandler.handle(command);

      res.status(200).json({
        success: true,
        data: BookingResponseMapper.fromDomain(booking),
      });
    } catch (error) {
      this.handleError(error, res);
    }
  }

  /**
   * POST /api/v1/bookings/:id/cancel
   * Cancels a booking
   */
  private async cancelBooking(req: Request, res: Response): Promise<void> {
    try {
      const reason = req.body.reason || 'Cancelled by user';
      const command = new CancelBookingCommand(req.params.id, reason);
      const booking = await this.cancelBookingHandler.handle(command);

      res.status(200).json({
        success: true,
        data: BookingResponseMapper.fromDomain(booking),
      });
    } catch (error) {
      this.handleError(error, res);
    }
  }

  /**
   * GET /api/v1/bookings/:id
   * Gets booking details by ID
   */
  private async getBookingById(req: Request, res: Response): Promise<void> {
    try {
      const query = new GetBookingByIdQuery(req.params.id);
      const booking = await this.getBookingByIdHandler.handle(query);

      res.status(200).json({
        success: true,
        data: BookingResponseMapper.fromDomain(booking),
      });
    } catch (error) {
      this.handleError(error, res);
    }
  }

  /**
   * GET /api/v1/bookings/user/:userId
   * Gets all bookings for a user
   */
  private async getBookingsByUser(req: Request, res: Response): Promise<void> {
    try {
      const query = new GetBookingsByUserQuery(req.params.userId);
      const bookings = await this.getBookingsByUserHandler.handle(query);

      res.status(200).json({
        success: true,
        data: BookingResponseMapper.fromDomainList(bookings),
        count: bookings.length,
      });
    } catch (error) {
      this.handleError(error, res);
    }
  }

  /**
   * GET /api/v1/bookings/event/:eventId
   * Gets all bookings for an event
   */
  private async getBookingsByEvent(req: Request, res: Response): Promise<void> {
    try {
      const query = new GetBookingsByEventQuery(req.params.eventId);
      const bookings = await this.getBookingsByEventHandler.handle(query);

      res.status(200).json({
        success: true,
        data: BookingResponseMapper.fromDomainList(bookings),
        count: bookings.length,
      });
    } catch (error) {
      this.handleError(error, res);
    }
  }

  /**
   * Error handler
   */
  private handleError(error: unknown, res: Response): void {
    console.error('Error:', error);

    if (error instanceof BookingNotFoundException) {
      res.status(404).json({
        success: false,
        error: 'Booking not found',
        message: error.message,
      });
      return;
    }

    if (error instanceof InvalidBookingStateException) {
      res.status(400).json({
        success: false,
        error: 'Invalid booking state',
        message: error.message,
      });
      return;
    }

    // Zod validation errors
    if (error && typeof error === 'object' && 'issues' in error) {
      res.status(400).json({
        success: false,
        error: 'Validation error',
        details: error,
      });
      return;
    }

    // Generic error
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  getRouter(): Router {
    return this.router;
  }
}
