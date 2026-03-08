package com.eventmanagement.eventservice.infrastructure.persistence;

import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * PostgreSQL Adapter - Implementa el Port del dominio usando JPA.
 */
@Component
@Transactional
public class PostgresEventRepositoryAdapter implements EventRepository {
    
    private final JpaEventRepository jpaRepository;
    private final EventMapper mapper;
    
    public PostgresEventRepositoryAdapter(
        JpaEventRepository jpaRepository,
        EventMapper mapper
    ) {
        this.jpaRepository = jpaRepository;
        this.mapper = mapper;
    }
    
    @Override
    public Event save(Event event) {
        EventEntity entity = mapper.toEntity(event);
        EventEntity savedEntity = jpaRepository.save(entity);
        return mapper.toDomain(savedEntity);
    }
    
    @Override
    public Optional<Event> findById(EventId id) {
        Optional<EventEntity> entityOpt = jpaRepository.findById(id.value());
        return entityOpt.map(mapper::toDomain);
    }
    
    @Override
    public List<Event> findAll() {
        return jpaRepository.findAll().stream()
            .map(mapper::toDomain)
            .collect(Collectors.toList());
    }
}
