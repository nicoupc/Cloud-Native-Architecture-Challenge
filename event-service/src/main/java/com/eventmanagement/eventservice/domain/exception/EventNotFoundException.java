package com.eventmanagement.eventservice.domain.exception;

import com.eventmanagement.eventservice.domain.model.EventId;

/**
 * EventNotFoundException - Error cuando no se encuentra un evento.
 * 
 * ¿Cuándo se lanza?
 * - Cuando intentas publicar un evento que no existe
 * - Cuando intentas actualizar un evento que fue eliminado
 * - Cuando el ID proporcionado es inválido
 * 
 * HTTP Status Code: 404 Not Found
 */
public class EventNotFoundException extends RuntimeException {
    
    private final EventId eventId;
    
    public EventNotFoundException(EventId eventId) {
        super("Event not found with id: " + eventId.value());
        this.eventId = eventId;
    }
    
    public EventId getEventId() {
        return eventId;
    }
}
