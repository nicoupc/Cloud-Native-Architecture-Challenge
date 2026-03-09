package com.eventmanagement.eventservice.infrastructure.persistence;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * JPA Entity para persistir Events en PostgreSQL.
 * 
 * Esta es la REPRESENTACIÓN DE BASE DE DATOS del Event.
 * NO es el Event del dominio.
 * 
 * Analogía:
 * - Event (dominio) = La persona real
 * - EventEntity (JPA) = La foto de la persona en la base de datos
 */
@Entity
@Table(name = "events", indexes = {
    @Index(name = "idx_event_status", columnList = "status"),
    @Index(name = "idx_event_date", columnList = "event_date"),
    @Index(name = "idx_event_type", columnList = "type")
})
public class EventEntity {
    
    @Id
    @Column(name = "id", nullable = false)
    private UUID id;
    
    @Column(name = "name", nullable = false, length = 200)
    private String name;
    
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;
    
    @Column(name = "type", nullable = false, length = 50)
    @Enumerated(EnumType.STRING)
    private EventTypeEnum type;
    
    @Column(name = "venue_id", nullable = false)
    private UUID venueId;
    
    @Column(name = "event_date", nullable = false)
    private LocalDateTime eventDate;
    
    @Column(name = "location_venue", nullable = false, length = 200)
    private String locationVenue;
    
    @Column(name = "location_city", nullable = false, length = 100)
    private String locationCity;
    
    @Column(name = "location_country", nullable = false, length = 100)
    private String locationCountry;
    
    @Column(name = "total_capacity", nullable = false)
    private Integer totalCapacity;
    
    @Column(name = "available_capacity", nullable = false)
    private Integer availableCapacity;
    
    @Column(name = "price_amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal priceAmount;
    
    @Column(name = "price_currency", nullable = false, length = 3)
    private String priceCurrency;
    
    @Column(name = "status", nullable = false, length = 50)
    @Enumerated(EnumType.STRING)
    private EventStatusEnum status;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;
    
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;
    
    // Constructor vacío requerido por JPA
    protected EventEntity() {
    }
    
    // Constructor con todos los campos
    public EventEntity(
        UUID id,
        String name,
        String description,
        EventTypeEnum type,
        UUID venueId,
        LocalDateTime eventDate,
        String locationVenue,
        String locationCity,
        String locationCountry,
        Integer totalCapacity,
        Integer availableCapacity,
        BigDecimal priceAmount,
        String priceCurrency,
        EventStatusEnum status,
        Instant createdAt,
        Instant updatedAt
    ) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.type = type;
        this.venueId = venueId;
        this.eventDate = eventDate;
        this.locationVenue = locationVenue;
        this.locationCity = locationCity;
        this.locationCountry = locationCountry;
        this.totalCapacity = totalCapacity;
        this.availableCapacity = availableCapacity;
        this.priceAmount = priceAmount;
        this.priceCurrency = priceCurrency;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    
    // Getters
    public UUID getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public EventTypeEnum getType() { return type; }
    public UUID getVenueId() { return venueId; }
    public LocalDateTime getEventDate() { return eventDate; }
    public String getLocationVenue() { return locationVenue; }
    public String getLocationCity() { return locationCity; }
    public String getLocationCountry() { return locationCountry; }
    public Integer getTotalCapacity() { return totalCapacity; }
    public Integer getAvailableCapacity() { return availableCapacity; }
    public BigDecimal getPriceAmount() { return priceAmount; }
    public String getPriceCurrency() { return priceCurrency; }
    public EventStatusEnum getStatus() { return status; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    
    // Setters (solo para campos mutables)
    public void setName(String name) { this.name = name; }
    public void setDescription(String description) { this.description = description; }
    public void setEventDate(LocalDateTime eventDate) { this.eventDate = eventDate; }
    public void setAvailableCapacity(Integer availableCapacity) { this.availableCapacity = availableCapacity; }
    public void setStatus(EventStatusEnum status) { this.status = status; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
    
    // Enums para JPA
    public enum EventTypeEnum {
        CONCERT, CONFERENCE, SPORTS
    }
    
    public enum EventStatusEnum {
        DRAFT, PUBLISHED, CANCELLED
    }
}
