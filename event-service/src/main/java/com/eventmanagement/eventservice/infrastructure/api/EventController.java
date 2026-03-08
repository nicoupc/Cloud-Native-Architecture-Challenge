package com.eventmanagement.eventservice.infrastructure.api;

import com.eventmanagement.eventservice.application.service.CreateEventService;
import com.eventmanagement.eventservice.domain.model.*;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * REST Controller - El "mostrador" donde llegan las peticiones HTTP.
 * 
 * Analogía: Esto es como el mesero de un restaurante:
 * - Recibe pedidos (HTTP requests)
 * - Los pasa a la cocina (CreateEventService)
 * - Devuelve la comida (HTTP response)
 */
@RestController
@RequestMapping("/api/v1/events")
public class EventController {

    private final CreateEventService createEventService;
    private final com.eventmanagement.eventservice.application.service.PublishEventService publishEventService;

    /**
     * Constructor Injection - Spring Boot inyecta automáticamente los servicios.
     * Es como si el restaurante te asignara automáticamente un chef.
     */
    public EventController(
        CreateEventService createEventService,
        com.eventmanagement.eventservice.application.service.PublishEventService publishEventService
    ) {
        this.createEventService = createEventService;
        this.publishEventService = publishEventService;
    }

    /**
     * POST /api/v1/events - Crear un nuevo evento
     * 
     * Ejemplo de petición:
     * POST http://localhost:8080/api/v1/events
     * Body: {
     *   "name": "Rock Concert",
     *   "description": "Amazing rock concert",
     *   "type": "CONCERT",
     *   "eventDate": "2026-12-31T20:00:00",
     *   "capacity": 1000,
     *   "price": 50.00
     * }
     */
    @PostMapping
    public ResponseEntity<EventResponse> createEvent(@RequestBody CreateEventRequest request) {
        // Usar venueId del request, o generar uno temporal si no viene
        EventId venueId = (request.venueId() != null && !request.venueId().isBlank())
            ? new EventId(java.util.UUID.fromString(request.venueId()))
            : EventId.generate();
        
        Event event = Event.create(
            request.name(),
            request.description(),
            request.type(),
            venueId,
            request.eventDate(),
            new Capacity(request.capacity()),
            new Price(new BigDecimal(request.price()), "USD")
        );

        // 2. Llamar al servicio de aplicación
        Event savedEvent = createEventService.execute(event);

        // 3. Convertir el evento del dominio a respuesta HTTP
        EventResponse response = new EventResponse(
            savedEvent.getId().value().toString(),
            savedEvent.getName(),
            savedEvent.getDescription(),
            savedEvent.getType().toString(),
            savedEvent.getEventDate().toString(),
            savedEvent.getTotalCapacity().value(),
            savedEvent.getPrice().amount().toString(),
            savedEvent.getStatus().toString()
        );

        // 4. Devolver respuesta con código 201 (Created)
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * POST /api/v1/events/{id}/publish - Publicar un evento
     * 
     * Ejemplo de petición:
     * POST http://localhost:8080/api/v1/events/123e4567-e89b-12d3-a456-426614174000/publish
     */
    @PostMapping("/{id}/publish")
    public ResponseEntity<EventResponse> publishEvent(@PathVariable String id) {
        // 1. Convertir String a EventId
        EventId eventId = new EventId(java.util.UUID.fromString(id));
        
        // 2. Llamar al servicio de aplicación
        Event publishedEvent = publishEventService.execute(eventId);
        
        // 3. Convertir el evento del dominio a respuesta HTTP
        EventResponse response = new EventResponse(
            publishedEvent.getId().value().toString(),
            publishedEvent.getName(),
            publishedEvent.getDescription(),
            publishedEvent.getType().toString(),
            publishedEvent.getEventDate().toString(),
            publishedEvent.getTotalCapacity().value(),
            publishedEvent.getPrice().amount().toString(),
            publishedEvent.getStatus().toString()
        );
        
        // 4. Devolver respuesta con código 200 (OK)
        return ResponseEntity.ok(response);
    }
    
    /**
     * GET /api/v1/events/health - Endpoint simple para verificar que funciona
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Event Service is running!");
    }
}

/**
 * DTO para recibir datos del cliente (Request)
 */
record CreateEventRequest(
    String name,
    String description,
    EventType type,
    LocalDateTime eventDate,
    int capacity,
    String price,
    String venueId
) {}

/**
 * DTO para enviar datos al cliente (Response)
 */
record EventResponse(
    String id,
    String name,
    String description,
    String type,
    String eventDate,
    int capacity,
    String price,
    String status
) {}
