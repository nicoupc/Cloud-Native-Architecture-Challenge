package com.eventmanagement.eventservice.infrastructure.persistence;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.UUID;

/**
 * JPA Repository - Spring Data genera la implementación automáticamente.
 * 
 * ¿Qué hace Spring Data?
 * - Genera automáticamente los métodos CRUD
 * - findById, save, delete, etc. ya están implementados
 * - Solo defines la interface, Spring hace la magia
 * 
 * Analogía:
 * - Tú defines el "contrato" (interface)
 * - Spring Data es el "empleado" que hace el trabajo
 */
@Repository
public interface JpaEventRepository extends JpaRepository<EventEntity, UUID> {
    
    // Spring Data genera automáticamente:
    // - save(EventEntity entity)
    // - findById(UUID id)
    // - findAll()
    // - delete(EventEntity entity)
    // - etc.
    
    // Puedes agregar métodos personalizados si necesitas:
    // List<EventEntity> findByStatus(EventStatusEnum status);
    // List<EventEntity> findByEventDateAfter(LocalDateTime date);
}
