package com.eventmanagement.eventservice.domain.model;

public record Location(String venue, String city, String country) {

    public Location {
        if (venue == null || venue.isBlank()) {
            throw new IllegalArgumentException("El venue no puede estar vacio");
        }
        if (city == null || city.isBlank()) {
            throw new IllegalArgumentException("La ciudad no puede estar vacia");
        }
        if (country == null || country.isBlank()) {
            throw new IllegalArgumentException("El pais no puede estar vacio");
        }
    }

    @Override
    public String toString() {
        return venue + ", " + city + ", " + country;
    }
}