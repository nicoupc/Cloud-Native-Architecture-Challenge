package com.eventmanagement.eventservice.domain.model;

/**
 * Value Object que representa la capacidad de un evento.
 * 
 * Regla de negocio: La capacidad NUNCA puede ser negativa.
 * Esta validación está en el DOMINIO, no en la base de datos.
 */
public record Capacity(int value) {
    
    /**
     * Constructor compacto con validación.
     * Si intentas crear Capacity(-10), lanza excepción.
     */
    public Capacity {
        if (value < 0) {
            throw new IllegalArgumentException(
                "La capacidad no puede ser negativa. Valor recibido: " + value
            );
        }
    }
    
    /**
     * Método de negocio: ¿Hay capacidad disponible?
     * Uso: if (capacity.isAvailable()) { ... }
     */
    public boolean isAvailable() {
        return value > 0;
    }
    
    /**
     * Método de negocio: Reducir capacidad.
     * Retorna un NUEVO Capacity (inmutable).
     * 
     * Ejemplo:
     * Capacity original = new Capacity(100);
     * Capacity nueva = original.reduce(10); // nueva = 90, original sigue siendo 100
     */
    public Capacity reduce(int amount) {
        if (amount < 0) {
            throw new IllegalArgumentException("No puedes reducir por un valor negativo");
        }
        return new Capacity(this.value - amount);
    }
}
