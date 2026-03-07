package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.event.EventPublished;
import com.eventmanagement.eventservice.domain.exception.EventNotFoundException;
import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import com.eventmanagement.eventservice.domain.port.EventPublisher;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * PublishEventService - Use Case para publicar un evento.
 * 
 * ¿Qué hace este servicio?
 * 1. Carga el evento desde la base de datos
 * 2. Llama al método publish() del dominio (DRAFT → PUBLISHED)
 * 3. Guarda el evento actualizado
 * 4. Publica EventPublished a EventBridge
 * 
 * ¿Por qué @Transactional?
 * - Si EventBridge falla, hace ROLLBACK de la base de datos
 * - Garantiza consistencia: o se publica TODO o NADA
 * 
 * Analogía:
 * - Es como publicar un libro:
 *   1. Verificas que el manuscrito existe
 *   2. Lo marcas como "Publicado"
 *   3. Lo guardas en el archivo
 *   4. Anunciar al mundo: "¡Nuevo libro disponible!"
 *   5. Si falla el anuncio, cancelas todo
 * 
 * Event-Driven Architecture:
 * - Este servicio emite EventPublished
 * - Booking Service lo escucha y habilita reservas
 * - Notification Service lo escucha y envía emails
 */
@Service
@Transactional
public class PublishEventService {
    
    private final EventRepository eventRepository;
    private final EventPublisher eventPublisher;
    
    /**
     * Constructor con inyección de dependencias.
     * Spring Boot inyecta automáticamente los adapters.
     */
    public PublishEventService(
        EventRepository eventRepository,
        EventPublisher eventPublisher
    ) {
        this.eventRepository = eventRepository;
        this.eventPublisher = eventPublisher;
    }
    
    /**
     * Ejecuta el use case de publicar un evento.
     * 
     * @param eventId ID del evento a publicar
     * @return El evento publicado
     * @throws EventNotFoundException si el evento no existe
     * @throws InvalidEventStateException si el evento no está en DRAFT
     * @throws EventPublishingException si falla la publicación a EventBridge
     */
    public Event execute(EventId eventId) {
        // 1. Cargar el evento desde la base de datos
        Event event = eventRepository.findById(eventId)
            .orElseThrow(() -> new EventNotFoundException(eventId));
        
        // 2. Llamar al método del dominio (valida estado y cambia a PUBLISHED)
        event.publish();
        
        // 3. Guardar el evento actualizado en la base de datos
        Event publishedEvent = eventRepository.save(event);
        
        // 4. Publicar evento de dominio a EventBridge
        // Si esto falla, @Transactional hace rollback automático
        EventPublished domainEvent = EventPublished.from(publishedEvent);
        eventPublisher.publish(domainEvent);
        
        return publishedEvent;
    }
}
