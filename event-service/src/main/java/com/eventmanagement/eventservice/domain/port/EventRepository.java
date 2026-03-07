package com.eventmanagement.eventservice.domain.port;

import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
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
    
    /**
     * Guarda un evento.
     * @param event El evento a guardar
     * @return El evento guardado (con ID generado si es nuevo)
     */
    Event save(Event event);
    
    /**
     * Busca un evento por su ID.
     * @param id El ID del evento
     * @return Optional con el evento si existe, Optional.empty() si no
     * 
     * ¿Qué es Optional?
     * - Es como una caja que puede estar vacía o tener algo
     * - Evita NullPointerException
     * - Uso: 
     *   Optional<Event> result = repository.findById(id);
     *   if (result.isPresent()) {
     *       Event event = result.get();
     *   }
     */
    Optional<Event> findById(EventId id);
}
