package com.eventmanagement.eventservice.infrastructure.persistence;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "venues")
public class VenueEntity {
    
    @Id
    @Column(name = "id", nullable = false)
    private UUID id;
    
    @Column(name = "name", nullable = false, length = 200)
    private String name;
    
    @Column(name = "address", length = 500)
    private String address;
    
    @Column(name = "city", nullable = false, length = 100)
    private String city;
    
    @Column(name = "country", nullable = false, length = 100)
    private String country;
    
    @Column(name = "max_capacity", nullable = false)
    private Integer maxCapacity;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;
    
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;
    
    protected VenueEntity() {}
    
    public VenueEntity(UUID id, String name, String address, String city, String country, Integer maxCapacity, Instant createdAt, Instant updatedAt) {
        this.id = id;
        this.name = name;
        this.address = address;
        this.city = city;
        this.country = country;
        this.maxCapacity = maxCapacity;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
    
    public UUID getId() { return id; }
    public String getName() { return name; }
    public String getAddress() { return address; }
    public String getCity() { return city; }
    public String getCountry() { return country; }
    public Integer getMaxCapacity() { return maxCapacity; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}