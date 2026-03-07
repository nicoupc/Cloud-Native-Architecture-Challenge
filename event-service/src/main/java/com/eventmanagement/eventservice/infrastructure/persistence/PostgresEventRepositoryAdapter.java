package com.eventmanagement.eventservice.infrastructure.persistence;

import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import java.util.Optional;

/**
 * PostgreSQL Adapter - Implementa el Port del dominio usando JPA.
 * 
 * Este es el ADAPTADOR que conecta:
 * - Domain (EventRepository port) ← → Infrastructure (PostgreSQL)
 * 
 * Hexagonal Architecture en acción:
 * - El dominio define QUÉ necesita (EventRepository interface)
 * - Este adapter define CÓMO lo hace (usando PostgreSQL + JPA)
 * 
 * Analogía:
 * - EventRepository = Enchufe estándar (110V)
 * - PostgresAdapter = Adaptador que conecta a la pared
 * - Puedes cambiar el adaptador sin cambiar el enchufe
 */
@Component
@Transactional
public class PostgresEventRepositoryAdapter implements EventRepository {
    
    private final JpaEventRepository jpaRepository;
    private final EventMapper mapper;
    
    /**
     * Constructor con inyección de dependencias.
     * Spring Boot inyecta automáticamente JpaEventRepository y EventMapper.
     */
    public PostgresEventRepositoryAdapter(
        JpaEventRepository jpaRepository,
        EventMapper mapper
    ) {
        this.jpaRepository = jpaRepository;
        this.mapper = mapper;
    }
    
    @Override
    public Event save(Event event) {
        // 1. Convertir Event (dominio) → EventEntity (JPA)
        EventEntity entity = mapper.toEntity(event);
        
        // 2. Guardar en PostgreSQL usando JPA
        EventEntity savedEntity = jpaRepository.save(entity);
        
        // 3. Convertir EventEntity (JPA) → Event (dominio)
        return mapper.toDomain(savedEntity);
    }
    
    @Override
    public Optional<Event> findById(EventId id) {
        // 1. Buscar en PostgreSQL usando JPA
        Optional<EventEntity> entityOpt = jpaRepository.findById(id.value());
        
        // 2. Si existe, convertir EventEntity → Event
        return entityOpt.map(mapper::toDomain);
    }
}
