package com.eventmanagement.eventservice.domain.exception;

/**
 * EventPublishingException - Error al publicar un evento de dominio.
 * 
 * ¿Cuándo se lanza?
 * - Cuando EventBridge no está disponible
 * - Cuando falla la conexión de red
 * - Cuando se excede el límite de reintentos
 * 
 * ¿Qué hacer cuando ocurre?
 * - Hacer rollback de la transacción
 * - Registrar el error en logs
 * - Notificar al equipo de operaciones
 */
public class EventPublishingException extends RuntimeException {
    
    public EventPublishingException(String message) {
        super(message);
    }
    
    public EventPublishingException(String message, Throwable cause) {
        super(message, cause);
    }
}
