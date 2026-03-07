package com.eventmanagement.eventservice.infrastructure.persistence;

import com.eventmanagement.eventservice.domain.model.*;
import org.springframework.stereotype.Component;

/**
 * Mapper: Convierte entre Event (dominio) y EventEntity (JPA).
 * 
 * ¿Por qué necesitamos esto?
 * - El dominio NO debe conocer JPA
 * - JPA NO debe contaminar el dominio
 * - Este mapper es el "traductor" entre ambos mundos
 * 
 * Analogía:
 * - Event = Persona hablando español
 * - EventEntity = Persona hablando inglés
 * - EventMapper = Traductor entre ambos
 */
@Component
public class EventMapper {
    
    /**
     * Convierte Event (dominio) → EventEntity (JPA)
     * Usado cuando queremos GUARDAR en la base de datos.
     */
    public EventEntity toEntity(Event event) {
        return new EventEntity(
            event.getId().value(),
            event.getName(),
            event.getDescription(),
            mapTypeToEnum(event.getType()),
            event.getVenueId().value(),
            event.getEventDate(),
            event.getTotalCapacity().value(),
            event.getAvailableCapacity().value(),
            event.getPrice().amount(),
            event.getPrice().currency(),
            mapStatusToEnum(event.getStatus()),
            event.getCreatedAt(),
            event.getUpdatedAt()
        );
    }
    
    /**
     * Convierte EventEntity (JPA) → Event (dominio)
     * Usado cuando queremos LEER de la base de datos.
     * 
     * Usamos Event.reconstruct() para recrear el objeto con TODOS sus datos.
     */
    public Event toDomain(EventEntity entity) {
        return Event.reconstruct(
            new EventId(entity.getId()),
            entity.getName(),
            entity.getDescription(),
            mapEnumToType(entity.getType()),
            new EventId(entity.getVenueId()),
            entity.getEventDate(),
            new Capacity(entity.getTotalCapacity()),
            new Capacity(entity.getAvailableCapacity()),
            new Price(entity.getPriceAmount(), entity.getPriceCurrency()),
            mapEnumToStatus(entity.getStatus()),
            entity.getCreatedAt(),
            entity.getUpdatedAt()
        );
    }
    
    // Mappers de enums
    private EventEntity.EventTypeEnum mapTypeToEnum(EventType type) {
        return EventEntity.EventTypeEnum.valueOf(type.name());
    }
    
    private EventType mapEnumToType(EventEntity.EventTypeEnum enumType) {
        return EventType.valueOf(enumType.name());
    }
    
    private EventEntity.EventStatusEnum mapStatusToEnum(EventStatus status) {
        return EventEntity.EventStatusEnum.valueOf(status.name());
    }
    
    private EventStatus mapEnumToStatus(EventEntity.EventStatusEnum enumStatus) {
        return EventStatus.valueOf(enumStatus.name());
    }
}
