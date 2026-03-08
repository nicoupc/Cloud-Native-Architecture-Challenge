package com.eventmanagement.eventservice.domain.model;

import java.time.Instant;
import java.time.LocalDateTime;

/**
 * Aggregate Root: Event
 * 
 * Representa un evento (concierto, conferencia, deporte) con todas sus reglas de negocio.
 * 
 * ¿Por qué es una clase y no un record?
 * - Porque su estado PUEDE cambiar (DRAFT → PUBLISHED → CANCELLED)
 * - Tiene comportamiento complejo (métodos de negocio)
 */
public class Event {
    
    // Atributos privados (nadie puede cambiarlos directamente)
    private final EventId id;
    private String name;
    private String description;
    private final EventType type;
    private final EventId venueId;
    private final LocalDateTime eventDate;
    private final Capacity totalCapacity;
    private Capacity availableCapacity;
    private Price price;
    private EventStatus status;
    private Instant createdAt;
    private Instant updatedAt;
    
    /**
     * Constructor privado.
     * Solo se puede crear un Event usando Event.create() o Event.reconstruct().
     */
    private Event(
        EventId id,
        String name,
        String description,
        EventType type,
        EventId venueId,
        LocalDateTime eventDate,
        Capacity totalCapacity,
        Price price
    ) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.type = type;
        this.venueId = venueId;
        this.eventDate = eventDate;
        this.totalCapacity = totalCapacity;
        this.availableCapacity = totalCapacity; // Al inicio, toda la capacidad está disponible
        this.price = price;
        this.status = EventStatus.DRAFT; // Siempre empieza en DRAFT
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
    }
    
    /**
     * Reconstruction Method: Usado SOLO por el mapper para reconstruir desde DB.
     * 
     * ¿Por qué existe esto?
     * - Cuando leemos de la DB, necesitamos recrear el Event con TODOS sus datos
     * - Incluyendo status, availableCapacity, createdAt, updatedAt
     * - Este método NO valida (asumimos que los datos de DB son válidos)
     */
    public static Event reconstruct(
        EventId id,
        String name,
        String description,
        EventType type,
        EventId venueId,
        LocalDateTime eventDate,
        Capacity totalCapacity,
        Capacity availableCapacity,
        Price price,
        EventStatus status,
        Instant createdAt,
        Instant updatedAt
    ) {
        Event event = new Event(id, name, description, type, venueId, eventDate, totalCapacity, price);
        event.availableCapacity = availableCapacity;
        event.status = status;
        event.createdAt = createdAt;
        event.updatedAt = updatedAt;
        return event;
    }
    
    /**
     * Factory Method: Forma correcta de crear un Event.
     * 
     * Uso:
     * Event event = Event.create(
     *     "Concierto Coldplay",
     *     "Descripción...",
     *     EventType.CONCERT,
     *     venueId,
     *     LocalDateTime.of(2024, 12, 31, 20, 0),
     *     new Capacity(5000),
     *     Price.usd(75.00)
     * );
     */
    public static Event create(
        String name,
        String description,
        EventType type,
        EventId venueId,
        LocalDateTime eventDate,
        Capacity totalCapacity,
        Price price
    ) {
        // Validaciones de negocio
        validateName(name);
        validateEventDate(eventDate);
        
        return new Event(
            EventId.generate(),
            name,
            description,
            type,
            venueId,
            eventDate,
            totalCapacity,
            price
        );
    }
    
    /**
     * Método de negocio: Publicar evento.
     * Solo eventos DRAFT pueden publicarse.
     */
    public void publish() {
        if (this.status != EventStatus.DRAFT) {
            throw new IllegalStateException(
                "Solo eventos en estado DRAFT pueden publicarse. Estado actual: " + this.status
            );
        }
        this.status = EventStatus.PUBLISHED;
        this.updatedAt = Instant.now();
    }
    
    /**
     * Método de negocio: Cancelar evento.
     * Solo eventos DRAFT o PUBLISHED pueden cancelarse.
     */
    public void cancel() {
        if (this.status == EventStatus.CANCELLED) {
            throw new IllegalStateException("El evento ya está cancelado");
        }
        this.status = EventStatus.CANCELLED;
        this.updatedAt = Instant.now();
    }
    
    // Validaciones privadas
    private static void validateName(String name) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("El nombre del evento no puede estar vacío");
        }
        if (name.length() > 200) {
            throw new IllegalArgumentException("El nombre no puede exceder 200 caracteres");
        }
    }
    
    private static void validateEventDate(LocalDateTime eventDate) {
        if (eventDate == null) {
            throw new IllegalArgumentException("La fecha del evento no puede ser null");
        }
        if (eventDate.isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("La fecha del evento debe ser futura");
        }
    }
    
    // Getters (solo lectura)
    public EventId getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public EventType getType() { return type; }
    public EventId getVenueId() { return venueId; }
    public LocalDateTime getEventDate() { return eventDate; }
    public Capacity getTotalCapacity() { return totalCapacity; }
    public Capacity getAvailableCapacity() { return availableCapacity; }
    public Price getPrice() { return price; }
    public EventStatus getStatus() { return status; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}
