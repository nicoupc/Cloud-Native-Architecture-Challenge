import { BookingResponseMapper } from '../BookingResponse';
import { Booking } from '../../../../domain/model/Booking';
import { UserId } from '../../../../domain/model/UserId';
import { EventId } from '../../../../domain/model/EventId';
import { TicketQuantity } from '../../../../domain/model/TicketQuantity';

describe('BookingResponseMapper', () => {
  it('should map domain booking to response', () => {
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(2),
      50.00
    );

    const response = BookingResponseMapper.fromDomain(booking);

    expect(response.id).toBe(booking.getId().getValue());
    expect(response.userId).toBe('user-123');
    expect(response.eventId).toBe('event-456');
    expect(response.status).toBe('PENDING');
    expect(response.ticketQuantity).toBe(2);
    expect(response.totalPrice).toBe(100.00);
    expect(response.createdAt).toBeDefined();
    expect(response.updatedAt).toBeDefined();
  });

  it('should map domain booking list to response list', () => {
    const booking1 = Booking.create(
      UserId.from('user-1'),
      EventId.from('event-1'),
      TicketQuantity.from(1),
      25.00
    );
    const booking2 = Booking.create(
      UserId.from('user-2'),
      EventId.from('event-2'),
      TicketQuantity.from(3),
      30.00
    );

    const responses = BookingResponseMapper.fromDomainList([booking1, booking2]);

    expect(responses).toHaveLength(2);
    expect(responses[0].userId).toBe('user-1');
    expect(responses[1].userId).toBe('user-2');
  });
});
