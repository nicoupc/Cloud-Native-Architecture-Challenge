package com.eventmanagement.eventservice.domain.model;

import java.time.LocalDateTime;

public record EventDate(LocalDateTime value) {

    public EventDate {
        if (value == null) {
            throw new IllegalArgumentException("La fecha del evento no puede ser null");
        }
    }

    public static EventDate ofFuture(LocalDateTime value) {
        if (value != null && value.isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("La fecha del evento debe ser futura");
        }
        return new EventDate(value);
    }

    @Override
    public String toString() {
        return value.toString();
    }
}