package com.eventmanagement.eventservice.infrastructure.config;

import com.eventmanagement.eventservice.application.service.CancelEventService;
import com.eventmanagement.eventservice.application.service.CreateEventService;
import com.eventmanagement.eventservice.application.service.GetEventService;
import com.eventmanagement.eventservice.application.service.PublishEventService;
import com.eventmanagement.eventservice.domain.port.EventPublisher;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ApplicationConfig {

    @Bean
    public CreateEventService createEventService(EventRepository eventRepository) {
        return new CreateEventService(eventRepository);
    }
    
    @Bean
    public PublishEventService publishEventService(
        EventRepository eventRepository,
        EventPublisher eventPublisher
    ) {
        return new PublishEventService(eventRepository, eventPublisher);
    }
    
    @Bean
    public CancelEventService cancelEventService(
        EventRepository eventRepository,
        EventPublisher eventPublisher
    ) {
        return new CancelEventService(eventRepository, eventPublisher);
    }
    
    @Bean
    public GetEventService getEventService(EventRepository eventRepository) {
        return new GetEventService(eventRepository);
    }
    
    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        return mapper;
    }
}
