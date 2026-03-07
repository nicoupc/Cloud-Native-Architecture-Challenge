package com.eventmanagement.eventservice.domain.event;

import com.eventmanagement.eventservice.domain.model.EventId;
import java.time.Instant;
import java.util.UUID;

/**
 * EventCreated - Evento de dominio que se emite cuando se crea un evento.
 * 
 * ¿Cuándo se emite?
 * - Cuando CreateEventService crea un nuevo evento
 * 
 * ¿Quién lo escucha?
 * - Booking Service (para crear índices de disponibilidad)
 * - Analytics Service (para métricas)
 * - Notification Service (para notificar a administradores)
 * 
 * Analogía:
 * - Es como un anuncio: "¡Se creó un nuevo concierto!"
 * - Otros servicios lo escuchan y reaccionan
 */
public record EventCreated(
    String eventId,
    String aggregateId,
    String eventName,
    String eventType,
    String eventDate,
    int totalCapacity,
    Instant occurredAt
) implements DomainEvent {
    
    /**
     * Factory method para crear el evento desde un Event aggregate
     */
    public static EventCreated from(
        com.eventmanagement.eventservice.domain.model.Event event
    ) {
        return new EventCreated(
            UUID.randomUUID().toString(),
            event.getId().value().toString(),
            event.getName(),
            event.getType().toString(),
            event.getEventDate().toString(),
            event.getTotalCapacity().value(),
            Instant.now()
        );
    }
    
    @Override
    public String eventType() {
        return "EventCreated";
    }
}
