package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.model.Venue;
import com.eventmanagement.eventservice.domain.model.VenueId;
import com.eventmanagement.eventservice.domain.port.VenueRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public class GetVenueService {
    
    private final VenueRepository venueRepository;
    
    public GetVenueService(VenueRepository venueRepository) {
        this.venueRepository = venueRepository;
    }
    
    public Optional<Venue> getById(UUID id) {
        return venueRepository.findById(new VenueId(id));
    }
    
    public List<Venue> getAll() {
        return venueRepository.findAll();
    }
}