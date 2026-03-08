package com.eventmanagement.eventservice.domain.port;

import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import java.util.List;
import java.util.Optional;

/**
 * Puerto (Interface) para persistir eventos.
 * 
 * ¿Por qué es una interface?
 * - El DOMINIO define QUÉ necesita (guardar, buscar)
 * - La INFRAESTRUCTURA decide CÓMO (PostgreSQL, MongoDB, memoria)
 * 
 * Esto es Hexagonal Architecture: el dominio no depende de la tecnología.
 */
public interface EventRepository {
    
    Event save(Event event);
    
    Optional<Event> findById(EventId id);
    
    List<Event> findAll();
}
