package com.eventmanagement.eventservice.domain.port;

import com.eventmanagement.eventservice.domain.event.DomainEvent;

/**
 * EventPublisher Port - Define CÓMO publicar eventos de dominio.
 * 
 * ¿Qué es un Port?
 * - Es una INTERFACE que define lo que el dominio necesita
 * - El dominio NO sabe CÓMO se implementa (EventBridge, Kafka, RabbitMQ)
 * - La infraestructura provee el ADAPTER que implementa este port
 * 
 * Hexagonal Architecture:
 * - Domain define: "Necesito publicar eventos" (este port)
 * - Infrastructure implementa: "Lo hago con EventBridge" (adapter)
 * 
 * Analogía:
 * - Port = Enchufe estándar (110V)
 * - Adapter = Cable que conecta a la pared
 * - Puedes cambiar el cable sin cambiar el enchufe
 */
public interface EventPublisher {
    
    /**
     * Publica un evento de dominio al bus de eventos.
     * 
     * @param event El evento a publicar (EventCreated, EventPublished, etc.)
     * @throws EventPublishingException si falla la publicación
     */
    void publish(DomainEvent event);
}
