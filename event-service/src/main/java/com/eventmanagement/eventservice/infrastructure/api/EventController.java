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

    /**
     * Constructor Injection - Spring Boot inyecta automáticamente el servicio.
     * Es como si el restaurante te asignara automáticamente un chef.
     */
    public EventController(CreateEventService createEventService) {
        this.createEventService = createEventService;
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
        // 1. Convertir el request HTTP a objetos del dominio
        // Por ahora usamos un venueId dummy (más adelante lo obtendremos del request)
        EventId dummyVenueId = EventId.generate();
        
        Event event = Event.create(
            request.name(),
            request.description(),
            request.type(),
            dummyVenueId,  // VenueId temporal
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
    String price
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
