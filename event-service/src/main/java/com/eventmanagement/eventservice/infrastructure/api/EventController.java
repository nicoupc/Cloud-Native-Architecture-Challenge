package com.eventmanagement.eventservice.infrastructure.api;

import com.eventmanagement.eventservice.application.service.CancelEventService;
import com.eventmanagement.eventservice.application.service.CreateEventService;
import com.eventmanagement.eventservice.application.service.GetEventService;
import com.eventmanagement.eventservice.domain.model.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/events")
public class EventController {

    private final CreateEventService createEventService;
    private final com.eventmanagement.eventservice.application.service.PublishEventService publishEventService;
    private final CancelEventService cancelEventService;
    private final GetEventService getEventService;

    public EventController(
        CreateEventService createEventService,
        com.eventmanagement.eventservice.application.service.PublishEventService publishEventService,
        CancelEventService cancelEventService,
        GetEventService getEventService
    ) {
        this.createEventService = createEventService;
        this.publishEventService = publishEventService;
        this.cancelEventService = cancelEventService;
        this.getEventService = getEventService;
    }

    /**
     * POST /api/v1/events - Create a new event
     */
    @PostMapping
    public ResponseEntity<EventResponse> createEvent(@Valid @RequestBody CreateEventRequest request) {
        EventId venueId = (request.venueId() != null && !request.venueId().isBlank())
            ? new EventId(java.util.UUID.fromString(request.venueId()))
            : EventId.generate();
        
        Event event = Event.create(
            request.name(),
            request.description(),
            request.type(),
            venueId,
            request.eventDate(),
            new Location(
                request.locationVenue() != null ? request.locationVenue() : "TBD",
                request.locationCity() != null ? request.locationCity() : "TBD",
                request.locationCountry() != null ? request.locationCountry() : "TBD"
            ),
            new Capacity(request.capacity()),
            new Price(new BigDecimal(request.price()), "USD")
        );

        Event savedEvent = createEventService.execute(event);
        return ResponseEntity.status(HttpStatus.CREATED).body(toResponse(savedEvent));
    }

    /**
     * POST /api/v1/events/{id}/publish - Publish an event
     */
    @PostMapping("/{id}/publish")
    public ResponseEntity<EventResponse> publishEvent(@PathVariable String id) {
        EventId eventId = new EventId(java.util.UUID.fromString(id));
        Event publishedEvent = publishEventService.execute(eventId);
        return ResponseEntity.ok(toResponse(publishedEvent));
    }

    /**
     * POST /api/v1/events/{id}/cancel - Cancel an event
     */
    @PostMapping("/{id}/cancel")
    public ResponseEntity<EventResponse> cancelEvent(
        @PathVariable String id,
        @RequestBody(required = false) CancelEventRequest request
    ) {
        EventId eventId = new EventId(java.util.UUID.fromString(id));
        String reason = (request != null && request.reason() != null) ? request.reason() : "No reason provided";
        Event cancelledEvent = cancelEventService.execute(eventId, reason);
        return ResponseEntity.ok(toResponse(cancelledEvent));
    }

    /**
     * GET /api/v1/events/{id} - Get event by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<EventResponse> getEvent(@PathVariable String id) {
        EventId eventId = new EventId(java.util.UUID.fromString(id));
        Event event = getEventService.getById(eventId);
        return ResponseEntity.ok(toResponse(event));
    }

    /**
     * GET /api/v1/events - List all events
     */
    @GetMapping
    public ResponseEntity<List<EventResponse>> listEvents() {
        List<Event> events = getEventService.getAll();
        List<EventResponse> responses = events.stream()
            .map(this::toResponse)
            .collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }

    /**
     * GET /api/v1/events/health - Health check
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Event Service is running!");
    }

    private EventResponse toResponse(Event event) {
        return new EventResponse(
            event.getId().value().toString(),
            event.getName(),
            event.getDescription(),
            event.getType().toString(),
            event.getEventDate().toString(),
            event.getLocation() != null ? event.getLocation().toString() : null,
            event.getTotalCapacity().value(),
            event.getAvailableCapacity().value(),
            event.getPrice().amount().toString(),
            event.getStatus().toString()
        );
    }
}

record CreateEventRequest(
    @NotBlank(message = "Event name is required")
    String name,

    @NotBlank(message = "Event description is required")
    String description,

    @NotNull(message = "Event type is required")
    EventType type,

    @NotNull(message = "Event date is required")
    LocalDateTime eventDate,

    @Positive(message = "Capacity must be greater than 0")
    int capacity,

    @NotBlank(message = "Price is required")
    String price,

    String venueId,
    String locationVenue,
    String locationCity,
    String locationCountry
) {}

record CancelEventRequest(
    String reason
) {}

record EventResponse(
    String id,
    String name,
    String description,
    String type,
    String eventDate,
    String location,
    int totalCapacity,
    int availableCapacity,
    String price,
    String status
) {}
