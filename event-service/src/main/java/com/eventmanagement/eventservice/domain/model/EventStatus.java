package com.eventmanagement.eventservice.domain.model;

/**
 * Enum que representa el estado de un evento.
 * 
 * Flujo de estados:
 * DRAFT → PUBLISHED → CANCELLED
 * 
 * Reglas:
 * - Solo eventos DRAFT pueden publicarse
 * - Solo eventos DRAFT o PUBLISHED pueden cancelarse
 * - Eventos CANCELLED no pueden cambiar de estado
 */
public enum EventStatus {
    DRAFT,      // Borrador, no visible para usuarios
    PUBLISHED,  // Publicado, visible y disponible para reservas
    CANCELLED   // Cancelado, no disponible
}
