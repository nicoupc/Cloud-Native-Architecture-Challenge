package com.eventmanagement.eventservice.domain.model;

import java.math.BigDecimal;

/**
 * Value Object que representa el precio de un evento.
 * 
 * ¿Por qué BigDecimal y no double?
 * - double tiene problemas de precisión: 0.1 + 0.2 = 0.30000000000000004
 * - BigDecimal es exacto: perfecto para dinero
 */
public record Price(BigDecimal amount, String currency) {
    
    /**
     * Constructor compacto con validaciones.
     */
    public Price {
        if (amount == null) {
            throw new IllegalArgumentException("El monto no puede ser null");
        }
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException(
                "El precio no puede ser negativo. Valor recibido: " + amount
            );
        }
        if (currency == null || currency.isBlank()) {
            throw new IllegalArgumentException("La moneda no puede estar vacía");
        }
    }
    
    /**
     * Método estático para crear un precio en USD.
     * Uso: Price price = Price.usd(75.00);
     */
    public static Price usd(double amount) {
        return new Price(BigDecimal.valueOf(amount), "USD");
    }
}
