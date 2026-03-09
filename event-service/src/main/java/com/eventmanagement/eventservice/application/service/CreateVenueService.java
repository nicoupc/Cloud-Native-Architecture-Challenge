package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.model.Venue;
import com.eventmanagement.eventservice.domain.port.VenueRepository;

public class CreateVenueService {
    
    private final VenueRepository venueRepository;
    
    public CreateVenueService(VenueRepository venueRepository) {
        this.venueRepository = venueRepository;
    }
    
    public Venue execute(String name, String address, String city, String country, int maxCapacity) {
        Venue venue = Venue.create(name, address, city, country, maxCapacity);
        return venueRepository.save(venue);
    }
}