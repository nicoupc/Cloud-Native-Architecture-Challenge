package com.eventmanagement.eventservice.domain.event;

import java.time.Instant;

/**
 * DomainEvent - Interfaz base para todos los eventos de dominio.
 * 
 * ¿Qué es un Domain Event?
 * - Es algo que YA PASÓ en el dominio (tiempo pasado)
 * - Comunica cambios importantes a otros servicios
 * - Es inmutable (no se puede cambiar después de crearse)
 * 
 * Analogía:
 * - Es como un periódico que anuncia: "¡Evento Publicado!"
 * - Una vez impreso, no puedes cambiar la noticia
 * - Otros servicios lo leen y reaccionan
 * 
 * Ejemplos:
 * - EventCreated (se creó un evento)
 * - EventPublished (se publicó un evento)
 * - EventCancelled (se canceló un evento)
 */
public sealed interface DomainEvent 
    permits EventCreated, EventPublished, EventCancelled {
    
    /**
     * Identificador único del evento de dominio
     */
    String eventId();
    
    /**
     * Timestamp de cuándo ocurrió el evento
     */
    Instant occurredAt();
    
    /**
     * Tipo de evento (para routing en EventBridge)
     */
    String eventType();
}
