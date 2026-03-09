package com.eventmanagement.eventservice.infrastructure.persistence;

import com.eventmanagement.eventservice.domain.model.Venue;
import com.eventmanagement.eventservice.domain.model.VenueId;
import com.eventmanagement.eventservice.domain.port.VenueRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
public class PostgresVenueRepositoryAdapter implements VenueRepository {
    
    private final JpaVenueRepository jpaRepository;
    private final VenueMapper mapper;
    
    public PostgresVenueRepositoryAdapter(JpaVenueRepository jpaRepository) {
        this.jpaRepository = jpaRepository;
        this.mapper = new VenueMapper();
    }
    
    @Override
    public Venue save(Venue venue) {
        VenueEntity entity = mapper.toEntity(venue);
        VenueEntity saved = jpaRepository.save(entity);
        return mapper.toDomain(saved);
    }
    
    @Override
    public Optional<Venue> findById(VenueId id) {
        return jpaRepository.findById(id.value()).map(mapper::toDomain);
    }
    
    @Override
    public List<Venue> findAll() {
        return jpaRepository.findAll().stream()
            .map(mapper::toDomain)
            .collect(Collectors.toList());
    }
}