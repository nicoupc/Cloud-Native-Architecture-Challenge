package com.eventmanagement.eventservice.infrastructure.persistence;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface JpaVenueRepository extends JpaRepository<VenueEntity, UUID> {
}