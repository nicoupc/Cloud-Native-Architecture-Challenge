package com.eventmanagement.eventservice.domain.model;

import java.util.UUID;

public record VenueId(UUID value) {
    public VenueId {
        if (value == null) {
            throw new IllegalArgumentException("VenueId no puede ser null");
        }
    }
    
    public static VenueId generate() {
        return new VenueId(UUID.randomUUID());
    }
}