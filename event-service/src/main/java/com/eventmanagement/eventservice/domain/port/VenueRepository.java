package com.eventmanagement.eventservice.domain.port;

import com.eventmanagement.eventservice.domain.model.Venue;
import com.eventmanagement.eventservice.domain.model.VenueId;
import java.util.List;
import java.util.Optional;

public interface VenueRepository {
    Venue save(Venue venue);
    Optional<Venue> findById(VenueId id);
    List<Venue> findAll();
}