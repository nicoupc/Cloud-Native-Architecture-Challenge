package com.eventmanagement.eventservice.domain.event;

import com.eventmanagement.eventservice.domain.model.Event;
import java.time.Instant;
import java.util.UUID;

/**
 * EventCancelled - Evento de dominio que se emite cuando se cancela un evento.
 * 
 * ¿Cuándo se emite?
 * - Cuando CancelEventService cambia el estado a CANCELLED
 * 
 * ¿Quién lo escucha?
 * - Booking Service (para cancelar todas las reservas)
 * - Payment Service (para procesar reembolsos)
 * - Notification Service (para notificar a usuarios con tickets)
 * 
 * Analogía:
 * - Es como anunciar: "¡El concierto se canceló!"
 * - Todos los que compraron tickets deben ser notificados y reembolsados
 */
public record EventCancelled(
    String eventId,
    String aggregateId,
    String eventName,
    String reason,
    Instant occurredAt
) implements DomainEvent {
    
    /**
     * Factory method para crear el evento desde un Event aggregate
     */
    public static EventCancelled from(Event event, String reason) {
        return new EventCancelled(
            event.getId().value().toString(),
            event.getId().value().toString(),
            event.getName(),
            reason,
            Instant.now()
        );
    }
    
    @Override
    public String eventType() {
        return "EventCancelled";
    }
}
