package com.eventmanagement.eventservice.infrastructure.config;

import com.eventmanagement.eventservice.application.service.CreateEventService;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import com.eventmanagement.eventservice.infrastructure.InMemoryEventRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuración de Spring Boot - El "panel eléctrico" que conecta todo.
 * 
 * Analogía: Esto es como el panel de fusibles de una casa:
 * - Define qué cables van a qué enchufes
 * - Spring Boot usa esto para saber cómo conectar las piezas
 */
@Configuration
public class ApplicationConfig {

    /**
     * @Bean le dice a Spring Boot: "Crea este objeto y guárdalo para usarlo después"
     * 
     * Cuando alguien necesite un EventRepository, Spring Boot dará este InMemoryEventRepository.
     */
    @Bean
    public EventRepository eventRepository() {
        return new InMemoryEventRepository();
    }

    /**
     * Cuando alguien necesite un CreateEventService, Spring Boot:
     * 1. Ve que necesita un EventRepository
     * 2. Busca el @Bean de arriba
     * 3. Lo inyecta automáticamente
     */
    @Bean
    public CreateEventService createEventService(EventRepository eventRepository) {
        return new CreateEventService(eventRepository);
    }
}
