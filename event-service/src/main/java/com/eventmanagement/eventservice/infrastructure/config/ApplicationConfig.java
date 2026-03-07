package com.eventmanagement.eventservice.infrastructure.config;

import com.eventmanagement.eventservice.application.service.CreateEventService;
import com.eventmanagement.eventservice.application.service.PublishEventService;
import com.eventmanagement.eventservice.domain.port.EventPublisher;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuración de Spring Boot - El "panel eléctrico" que conecta todo.
 * 
 * Analogía: Esto es como el panel de fusibles de una casa:
 * - Define qué cables van a qué enchufes
 * - Spring Boot usa esto para saber cómo conectar las piezas
 * 
 * IMPORTANTE: Ya NO necesitamos crear los repositories aquí.
 * Los adapters ya tienen @Component, así que Spring Boot
 * los detecta automáticamente y los inyecta donde se necesiten.
 */
@Configuration
public class ApplicationConfig {

    /**
     * CreateEventService - Use case para crear eventos
     */
    @Bean
    public CreateEventService createEventService(EventRepository eventRepository) {
        return new CreateEventService(eventRepository);
    }
    
    /**
     * PublishEventService - Use case para publicar eventos
     */
    @Bean
    public PublishEventService publishEventService(
        EventRepository eventRepository,
        EventPublisher eventPublisher
    ) {
        return new PublishEventService(eventRepository, eventPublisher);
    }
    
    /**
     * ObjectMapper - Para serializar/deserializar JSON
     * Configurado con soporte para Java 8 Time API (LocalDateTime, Instant, etc.)
     */
    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        return mapper;
    }
}
