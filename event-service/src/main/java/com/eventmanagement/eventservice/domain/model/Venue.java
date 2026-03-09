package com.eventmanagement.eventservice.domain.model;

import java.time.Instant;

/**
 * Aggregate Root: Venue
 * Represents a physical location where events take place.
 */
public class Venue {
    
    private final VenueId id;
    private String name;
    private String address;
    private String city;
    private String country;
    private int maxCapacity;
    private final Instant createdAt;
    private Instant updatedAt;
    
    private Venue(VenueId id, String name, String address, String city, String country, int maxCapacity, Instant createdAt, Instant updatedAt) {
        this.id = id;
        this.name = name;
        this.address = address;
        this.city = city;
        this.country = country;
        this.maxCapacity = maxCapacity;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    
    public static Venue create(String name, String address, String city, String country, int maxCapacity) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Venue name cannot be blank");
        }
        if (city == null || city.isBlank()) {
            throw new IllegalArgumentException("Venue city cannot be blank");
        }
        if (country == null || country.isBlank()) {
            throw new IllegalArgumentException("Venue country cannot be blank");
        }
        if (maxCapacity <= 0) {
            throw new IllegalArgumentException("Max capacity must be positive");
        }
        
        Instant now = Instant.now();
        return new Venue(VenueId.generate(), name, address != null ? address : "", city, country, maxCapacity, now, now);
    }
    
    public static Venue reconstruct(VenueId id, String name, String address, String city, String country, int maxCapacity, Instant createdAt, Instant updatedAt) {
        return new Venue(id, name, address, city, country, maxCapacity, createdAt, updatedAt);
    }
    
    // Getters
    public VenueId getId() { return id; }
    public String getName() { return name; }
    public String getAddress() { return address; }
    public String getCity() { return city; }
    public String getCountry() { return country; }
    public int getMaxCapacity() { return maxCapacity; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}