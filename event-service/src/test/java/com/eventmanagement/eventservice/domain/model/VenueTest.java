package com.eventmanagement.eventservice.domain.model;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

class VenueTest {
    
    @Test
    @DisplayName("Should create venue with valid data")
    void shouldCreateVenue() {
        Venue venue = Venue.create("Estadio Nacional", "Av. Jose Diaz", "Lima", "Peru", 50000);
        
        assertNotNull(venue.getId());
        assertEquals("Estadio Nacional", venue.getName());
        assertEquals("Av. Jose Diaz", venue.getAddress());
        assertEquals("Lima", venue.getCity());
        assertEquals("Peru", venue.getCountry());
        assertEquals(50000, venue.getMaxCapacity());
        assertNotNull(venue.getCreatedAt());
    }
    
    @Test
    @DisplayName("Should reject blank name")
    void shouldRejectBlankName() {
        assertThrows(IllegalArgumentException.class, () ->
            Venue.create("", "Av. Jose Diaz", "Lima", "Peru", 50000));
    }
    
    @Test
    @DisplayName("Should reject null city")
    void shouldRejectNullCity() {
        assertThrows(IllegalArgumentException.class, () ->
            Venue.create("Estadio", "Av.", null, "Peru", 50000));
    }
    
    @Test
    @DisplayName("Should reject zero capacity")
    void shouldRejectZeroCapacity() {
        assertThrows(IllegalArgumentException.class, () ->
            Venue.create("Estadio", "Av.", "Lima", "Peru", 0));
    }
    
    @Test
    @DisplayName("Should reject negative capacity")
    void shouldRejectNegativeCapacity() {
        assertThrows(IllegalArgumentException.class, () ->
            Venue.create("Estadio", "Av.", "Lima", "Peru", -100));
    }
    
    @Test
    @DisplayName("Should reconstruct venue from persistence")
    void shouldReconstructVenue() {
        VenueId id = VenueId.generate();
        java.time.Instant now = java.time.Instant.now();
        
        Venue venue = Venue.reconstruct(id, "Estadio", "Av.", "Lima", "Peru", 50000, now, now);
        
        assertEquals(id, venue.getId());
        assertEquals("Estadio", venue.getName());
        assertEquals(now, venue.getCreatedAt());
    }
    
    @Test
    @DisplayName("VenueId should generate unique IDs")
    void venueIdShouldBeUnique() {
        VenueId id1 = VenueId.generate();
        VenueId id2 = VenueId.generate();
        assertNotEquals(id1, id2);
    }
    
    @Test
    @DisplayName("VenueId should reject null")
    void venueIdShouldRejectNull() {
        assertThrows(IllegalArgumentException.class, () -> new VenueId(null));
    }
}