package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.model.*;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import java.time.LocalDateTime;

/**
 * Caso de Uso: Crear un evento.
 * 
 * Esta clase ORQUESTA el proceso:
 * 1. Recibe los datos
 * 2. Llama al dominio para crear el evento
 * 3. Guarda el evento usando el repositorio
 * 4. Retorna el evento creado
 * 
 * NO tiene lógica de negocio (eso está en Event)
 * NO sabe cómo se guarda (eso está en el adaptador)
 */
public class CreateEventService {
    
    private final EventRepository eventRepository;
    
    /**
     * Constructor con inyección de dependencias.
     * 
     * ¿Qué es inyección de dependencias?
     * - En vez de crear el repositorio aquí (new PostgresRepository())
     * - Lo recibimos como parámetro
     * - Así podemos cambiar la implementación sin tocar este código
     * 
     * Ejemplo:
     * - En producción: new CreateEventService(new PostgresRepository())
     * - En tests: new CreateEventService(new InMemoryRepository())
     */
    public CreateEventService(EventRepository eventRepository) {
        this.eventRepository = eventRepository;
    }
    
    /**
     * Ejecuta el caso de uso: crear evento.
     * 
     * @param event El evento a crear (ya validado por el dominio)
     * @return El evento creado y guardado
     */
    public Event execute(Event event) {
        // Guardar el evento usando el repositorio
        // (No sabemos si es PostgreSQL, MongoDB o memoria)
        return eventRepository.save(event);
    }
}
