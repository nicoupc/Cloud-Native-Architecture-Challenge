package com.eventmanagement.eventservice.infrastructure.config;

import com.eventmanagement.eventservice.application.service.CreateEventService;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuración de Spring Boot - El "panel eléctrico" que conecta todo.
 * 
 * Analogía: Esto es como el panel de fusibles de una casa:
 * - Define qué cables van a qué enchufes
 * - Spring Boot usa esto para saber cómo conectar las piezas
 * 
 * IMPORTANTE: Ya NO necesitamos crear el EventRepository aquí.
 * PostgresEventRepositoryAdapter ya tiene @Component, así que Spring Boot
 * lo detecta automáticamente y lo inyecta donde se necesite.
 */
@Configuration
public class ApplicationConfig {

    /**
     * Cuando alguien necesite un CreateEventService, Spring Boot:
     * 1. Ve que necesita un EventRepository
     * 2. Busca un @Component que implemente EventRepository
     * 3. Encuentra PostgresEventRepositoryAdapter
     * 4. Lo inyecta automáticamente
     */
    @Bean
    public CreateEventService createEventService(EventRepository eventRepository) {
        return new CreateEventService(eventRepository);
    }
}
