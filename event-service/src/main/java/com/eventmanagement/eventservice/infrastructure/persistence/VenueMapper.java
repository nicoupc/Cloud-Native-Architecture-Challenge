package com.eventmanagement.eventservice.infrastructure.persistence;

import com.eventmanagement.eventservice.domain.model.Venue;
import com.eventmanagement.eventservice.domain.model.VenueId;

public class VenueMapper {
    
    public VenueEntity toEntity(Venue venue) {
        return new VenueEntity(
            venue.getId().value(),
            venue.getName(),
            venue.getAddress(),
            venue.getCity(),
            venue.getCountry(),
            venue.getMaxCapacity(),
            venue.getCreatedAt(),
            venue.getUpdatedAt()
        );
    }
    
    public Venue toDomain(VenueEntity entity) {
        return Venue.reconstruct(
            new VenueId(entity.getId()),
            entity.getName(),
            entity.getAddress(),
            entity.getCity(),
            entity.getCountry(),
            entity.getMaxCapacity(),
            entity.getCreatedAt(),
            entity.getUpdatedAt()
        );
    }
}