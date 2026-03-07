package com.eventmanagement.eventservice.domain.event;

import com.eventmanagement.eventservice.domain.model.Event;
import java.time.Instant;
import java.util.UUID;

/**
 * EventPublished - Evento de dominio que se emite cuando se publica un evento.
 * 
 * ¿Cuándo se emite?
 * - Cuando PublishEventService cambia el estado de DRAFT → PUBLISHED
 * 
 * ¿Quién lo escucha?
 * - Booking Service (para habilitar reservas)
 * - Notification Service (para enviar emails a usuarios interesados)
 * - Search Service (para indexar en búsqueda)
 * 
 * Analogía:
 * - Es como anunciar: "¡El concierto ya está disponible para comprar tickets!"
 * - Los usuarios pueden empezar a reservar
 */
public record EventPublished(
    String eventId,
    String aggregateId,
    String eventName,
    String eventType,
    String eventDate,
    int availableCapacity,
    String price,
    Instant occurredAt
) implements DomainEvent {
    
    /**
     * Factory method para crear el evento desde un Event aggregate
     */
    public static EventPublished from(Event event) {
        return new EventPublished(
            UUID.randomUUID().toString(),
            event.getId().value().toString(),
            event.getName(),
            event.getType().toString(),
            event.getEventDate().toString(),
            event.getAvailableCapacity().value(),
            event.getPrice().amount().toString(),
            Instant.now()
        );
    }
    
    @Override
    public String eventType() {
        return "EventPublished";
    }
}
