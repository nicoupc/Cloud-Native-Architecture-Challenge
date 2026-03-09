import { BookingMapper, DynamoDBBookingItem } from '../BookingMapper';
import { Booking } from '../../../domain/model/Booking';
import { UserId } from '../../../domain/model/UserId';
import { EventId } from '../../../domain/model/EventId';
import { BookingStatus } from '../../../domain/model/BookingStatus';
import { TicketQuantity } from '../../../domain/model/TicketQuantity';

describe('BookingMapper', () => {
  const fixedDate = new Date('2024-01-15T10:30:00.000Z');

  it('should map domain booking to DynamoDB item correctly', () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(3),
      50.00
    );

    // Act
    const item = BookingMapper.toDynamoDB(booking);

    // Assert
    expect(item.bookingId).toBe(booking.getId().getValue());
    expect(item.userId).toBe('user-123');
    expect(item.eventId).toBe('event-456');
    expect(item.status).toBe('PENDING');
    expect(item.ticketQuantity).toBe(3);
    expect(item.totalPrice).toBe(150.00);
    expect(item.createdAt).toBeDefined();
    expect(item.updatedAt).toBeDefined();
  });

  it('should set PK and SK correctly (BOOKING#{bookingId})', () => {
    // Arrange
    const booking = Booking.create(
      UserId.from('user-123'),
      EventId.from('event-456'),
      TicketQuantity.from(1),
      25.00
    );
    const expectedKey = `BOOKING#${booking.getId().getValue()}`;

    // Act
    const item = BookingMapper.toDynamoDB(booking);

    // Assert
    expect(item.PK).toBe(expectedKey);
    expect(item.SK).toBe(expectedKey);
  });

  it('should map DynamoDB item to domain booking correctly', () => {
    // Arrange
    const item: DynamoDBBookingItem = {
      PK: 'BOOKING#booking-789',
      SK: 'BOOKING#booking-789',
      bookingId: 'booking-789',
      userId: 'user-abc',
      eventId: 'event-def',
      status: 'CONFIRMED',
      ticketQuantity: 5,
      totalPrice: 250.00,
      createdAt: fixedDate.toISOString(),
      updatedAt: fixedDate.toISOString(),
    };

    // Act
    const booking = BookingMapper.toDomain(item);

    // Assert
    expect(booking).toBeInstanceOf(Booking);
    expect(booking.getId().getValue()).toBe('booking-789');
    expect(booking.getUserId().getValue()).toBe('user-abc');
    expect(booking.getEventId().getValue()).toBe('event-def');
    expect(booking.getStatus()).toBe(BookingStatus.CONFIRMED);
    expect(booking.getTicketQuantity().getValue()).toBe(5);
    expect(booking.getTotalPrice().getAmount()).toBe(250.00);
    expect(booking.getCreatedAt()).toEqual(fixedDate);
    expect(booking.getUpdatedAt()).toEqual(fixedDate);
  });

  it('should preserve all fields in round-trip conversion', () => {
    // Arrange
    const original = Booking.create(
      UserId.from('user-round-trip'),
      EventId.from('event-round-trip'),
      TicketQuantity.from(4),
      30.00
    );

    // Act: Domain → DynamoDB → Domain
    const dynamoItem = BookingMapper.toDynamoDB(original);
    const restored = BookingMapper.toDomain(dynamoItem);

    // Assert
    expect(restored.getId().getValue()).toBe(original.getId().getValue());
    expect(restored.getUserId().getValue()).toBe(original.getUserId().getValue());
    expect(restored.getEventId().getValue()).toBe(original.getEventId().getValue());
    expect(restored.getStatus()).toBe(original.getStatus());
    expect(restored.getTicketQuantity().getValue()).toBe(original.getTicketQuantity().getValue());
    expect(restored.getTotalPrice().getAmount()).toBe(original.getTotalPrice().getAmount());
    expect(restored.getCreatedAt().toISOString()).toBe(original.getCreatedAt().toISOString());
    expect(restored.getUpdatedAt().toISOString()).toBe(original.getUpdatedAt().toISOString());
  });
});
