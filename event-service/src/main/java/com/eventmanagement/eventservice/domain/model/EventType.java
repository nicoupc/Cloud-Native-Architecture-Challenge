package com.eventmanagement.eventservice.domain.model;

/**
 * Enum que representa los tipos de eventos soportados.
 * 
 * ¿Por qué enum y no String?
 * - Evita errores de tipeo: "CONCRT" vs EventType.CONCERT
 * - El compilador valida que solo uses valores válidos
 * - Autocompletado en el IDE
 */
public enum EventType {
    CONCERT,
    CONFERENCE,
    SPORTS
}
