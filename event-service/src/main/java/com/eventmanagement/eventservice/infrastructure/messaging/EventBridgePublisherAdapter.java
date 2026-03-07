package com.eventmanagement.eventservice.infrastructure.messaging;

import com.eventmanagement.eventservice.domain.event.DomainEvent;
import com.eventmanagement.eventservice.domain.exception.EventPublishingException;
import com.eventmanagement.eventservice.domain.port.EventPublisher;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.services.eventbridge.EventBridgeClient;
import software.amazon.awssdk.services.eventbridge.model.PutEventsRequest;
import software.amazon.awssdk.services.eventbridge.model.PutEventsRequestEntry;
import software.amazon.awssdk.services.eventbridge.model.PutEventsResponse;

/**
 * EventBridgePublisherAdapter - Implementa el port EventPublisher usando AWS EventBridge.
 * 
 * ¿Qué es EventBridge?
 * - Es un "bus de eventos" de AWS
 * - Permite comunicación asíncrona entre servicios
 * - Otros servicios se "suscriben" a eventos específicos
 * 
 * Hexagonal Architecture:
 * - Domain define: "Necesito publicar eventos" (EventPublisher port)
 * - Este adapter implementa: "Lo hago con EventBridge"
 * 
 * Analogía:
 * - EventBridge = Estación de radio
 * - Este adapter = Transmisor que envía la señal
 * - Otros servicios = Radios que escuchan la frecuencia
 * 
 * ¿Por qué usar EventBridge?
 * - Desacopla servicios (no necesitan conocerse)
 * - Permite agregar nuevos servicios sin modificar existentes
 * - Soporta retry automático y dead-letter queues
 */
@Component
public class EventBridgePublisherAdapter implements EventPublisher {
    
    private static final Logger logger = LoggerFactory.getLogger(EventBridgePublisherAdapter.class);
    
    private final EventBridgeClient eventBridgeClient;
    private final ObjectMapper objectMapper;
    private final String eventBusName;
    private final String eventSource;
    
    /**
     * Constructor con inyección de dependencias.
     * 
     * @param eventBridgeClient Cliente de AWS SDK (configurado en AwsConfig)
     * @param objectMapper Para serializar eventos a JSON
     * @param eventBusName Nombre del bus de eventos (desde application.yml)
     * @param eventSource Fuente de los eventos (desde application.yml)
     */
    public EventBridgePublisherAdapter(
        EventBridgeClient eventBridgeClient,
        ObjectMapper objectMapper,
        @Value("${aws.eventbridge.bus-name}") String eventBusName,
        @Value("${aws.eventbridge.source}") String eventSource
    ) {
        this.eventBridgeClient = eventBridgeClient;
        this.objectMapper = objectMapper;
        this.eventBusName = eventBusName;
        this.eventSource = eventSource;
    }
    
    @Override
    public void publish(DomainEvent event) {
        try {
            // 1. Serializar el evento a JSON
            String eventJson = objectMapper.writeValueAsString(event);
            
            logger.info("Publishing event to EventBridge: type={}, eventId={}", 
                event.eventType(), event.eventId());
            
            // 2. Crear la entrada para EventBridge
            PutEventsRequestEntry entry = PutEventsRequestEntry.builder()
                .eventBusName(eventBusName)
                .source(eventSource)
                .detailType(event.eventType())
                .detail(eventJson)
                .build();
            
            // 3. Enviar el evento a EventBridge
            PutEventsRequest request = PutEventsRequest.builder()
                .entries(entry)
                .build();
            
            PutEventsResponse response = eventBridgeClient.putEvents(request);
            
            // 4. Verificar si hubo errores
            if (response.failedEntryCount() > 0) {
                String errorMessage = response.entries().get(0).errorMessage();
                logger.error("Failed to publish event to EventBridge: {}", errorMessage);
                throw new EventPublishingException(
                    "Failed to publish event: " + errorMessage
                );
            }
            
            logger.info("Event published successfully to EventBridge: eventId={}", 
                event.eventId());
            
        } catch (JsonProcessingException e) {
            logger.error("Failed to serialize event to JSON", e);
            throw new EventPublishingException("Failed to serialize event", e);
        } catch (Exception e) {
            logger.error("Unexpected error publishing event to EventBridge", e);
            throw new EventPublishingException("Failed to publish event", e);
        }
    }
}
