package com.eventmanagement.eventservice.domain.model;

import java.util.UUID;

/**
 * Value Object que representa el identificador único de un evento.
 * 
 * ¿Por qué es un record?
 * - Es inmutable (no puede cambiar después de crearse)
 * - Solo contiene datos, sin comportamiento complejo
 * - Perfecto para identificadores
 */
public record EventId(UUID value) {
    
    /**
     * Constructor compacto que valida el valor.
     * Se ejecuta automáticamente cuando creas un EventId.
     */
    public EventId {
        if (value == null) {
            throw new IllegalArgumentException("EventId no puede ser null");
        }
    }
    
    /**
     * Método estático para generar un nuevo ID aleatorio.
     * Uso: EventId id = EventId.generate();
     */
    public static EventId generate() {
        return new EventId(UUID.randomUUID());
    }
}
