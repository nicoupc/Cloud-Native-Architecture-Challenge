package com.eventmanagement.eventservice.infrastructure;

import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Implementación EN MEMORIA del EventRepository.
 * 
 * ¿Para qué sirve?
 * - Para tests (no necesitas base de datos)
 * - Para desarrollo rápido
 * - Para demostrar que el dominio NO depende de PostgreSQL
 * 
 * Implementa la MISMA interface que PostgresEventRepository.
 * El dominio no sabe cuál estás usando.
 */
public class InMemoryEventRepository implements EventRepository {
    
    // HashMap = diccionario en Python
    // Guarda eventos en memoria: {id: event}
    private final Map<EventId, Event> events = new HashMap<>();
    
    @Override
    public Event save(Event event) {
        // Guarda en el HashMap
        events.put(event.getId(), event);
        return event;
    }
    
    @Override
    public Optional<Event> findById(EventId id) {
        // Busca en el HashMap
        Event event = events.get(id);
        
        // Si existe, retorna Optional con el evento
        // Si no existe, retorna Optional vacío
        return Optional.ofNullable(event);
    }
    
    /**
     * Método helper para tests: limpiar todos los eventos.
     */
    public void clear() {
        events.clear();
    }
    
    /**
     * Método helper para tests: contar eventos guardados.
     */
    public int count() {
        return events.size();
    }
}
