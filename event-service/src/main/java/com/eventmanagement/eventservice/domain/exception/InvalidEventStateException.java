package com.eventmanagement.eventservice.domain.exception;

import com.eventmanagement.eventservice.domain.model.EventStatus;

/**
 * InvalidEventStateException - Error cuando se intenta una transición de estado inválida.
 * 
 * ¿Cuándo se lanza?
 * - Intentar publicar un evento que ya está PUBLISHED
 * - Intentar publicar un evento que está CANCELLED
 * - Intentar cancelar un evento que ya está CANCELLED
 * 
 * HTTP Status Code: 400 Bad Request
 */
public class InvalidEventStateException extends RuntimeException {
    
    private final EventStatus currentStatus;
    private final EventStatus attemptedStatus;
    
    public InvalidEventStateException(
        EventStatus currentStatus,
        EventStatus attemptedStatus
    ) {
        super(String.format(
            "Cannot transition from %s to %s",
            currentStatus,
            attemptedStatus
        ));
        this.currentStatus = currentStatus;
        this.attemptedStatus = attemptedStatus;
    }
    
    public EventStatus getCurrentStatus() {
        return currentStatus;
    }
    
    public EventStatus getAttemptedStatus() {
        return attemptedStatus;
    }
}
