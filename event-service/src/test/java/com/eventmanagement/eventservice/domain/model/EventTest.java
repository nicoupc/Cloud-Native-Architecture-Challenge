package com.eventmanagement.eventservice.domain.model;

import org.junit.jupiter.api.Test;
import java.time.LocalDateTime;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests para el Aggregate Event.
 * 
 * Los tests son la mejor documentación del código.
 * Aquí ves CÓMO usar Event y QUÉ esperar.
 */
class EventTest {
    
    /**
     * Test 1: Crear un evento válido.
     * Verifica que todos los valores se asignan correctamente.
     */
    @Test
    void shouldCreateEventSuccessfully() {
        // Arrange (Preparar datos)
        String name = "Concierto Coldplay";
        String description = "Concierto en vivo";
        EventType type = EventType.CONCERT;
        EventId venueId = EventId.generate();
        LocalDateTime eventDate = LocalDateTime.now().plusDays(30);
        Location location = new Location("Estadio Nacional", "Lima", "Peru");
        Capacity capacity = new Capacity(5000);
        Price price = Price.usd(75.00);
        
        // Act (Ejecutar acción)
        Event event = Event.create(name, description, type, venueId, eventDate, location, capacity, price);
        
        // Assert (Verificar resultados)
        assertNotNull(event.getId(), "El ID no debe ser null");
        assertEquals(name, event.getName(), "El nombre debe coincidir");
        assertEquals(description, event.getDescription());
        assertEquals(type, event.getType());
        assertEquals(venueId, event.getVenueId());
        assertEquals(eventDate, event.getEventDate().value());
        assertEquals(location, event.getLocation());
        assertEquals(capacity, event.getTotalCapacity());
        assertEquals(capacity, event.getAvailableCapacity(), "Capacidad disponible debe ser igual a total al inicio");
        assertEquals(price, event.getPrice());
        assertEquals(EventStatus.DRAFT, event.getStatus(), "Nuevos eventos deben estar en DRAFT");
    }
    
    /**
     * Test 2: No se puede crear evento con fecha pasada.
     * Verifica que la validación funciona.
     */
    @Test
    void shouldFailWhenEventDateIsInPast() {
        // Arrange
        LocalDateTime pastDate = LocalDateTime.now().minusDays(1); // Ayer
        
        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            Event.create(
                "Evento Pasado",
                "Descripción",
                EventType.CONCERT,
                EventId.generate(),
                pastDate, // ← Fecha inválida
                new Location("Venue", "City", "Country"),
                new Capacity(100),
                Price.usd(50.00)
            );
        }, "Debe lanzar excepción cuando la fecha es pasada");
    }
    
    /**
     * Test 3: No se puede crear evento con nombre vacío.
     */
    @Test
    void shouldFailWhenNameIsEmpty() {
        assertThrows(IllegalArgumentException.class, () -> {
            Event.create(
                "", // ← Nombre vacío
                "Descripción",
                EventType.CONCERT,
                EventId.generate(),
                LocalDateTime.now().plusDays(30),
                new Location("Venue", "City", "Country"),
                new Capacity(100),
                Price.usd(50.00)
            );
        });
    }
    
    /**
     * Test 4: Publicar evento DRAFT.
     * Verifica la transición de estado.
     */
    @Test
    void shouldPublishDraftEvent() {
        // Arrange
        Event event = createValidEvent();
        assertEquals(EventStatus.DRAFT, event.getStatus());
        
        // Act
        event.publish();
        
        // Assert
        assertEquals(EventStatus.PUBLISHED, event.getStatus(), "El evento debe estar PUBLISHED");
    }
    
    /**
     * Test 5: No se puede publicar evento que ya está PUBLISHED.
     */
    @Test
    void shouldFailWhenPublishingAlreadyPublishedEvent() {
        // Arrange
        Event event = createValidEvent();
        event.publish(); // Primera publicación (OK)
        
        // Act & Assert
        assertThrows(IllegalStateException.class, () -> {
            event.publish(); // Segunda publicación (FALLA)
        }, "No se puede publicar un evento ya publicado");
    }
    
    /**
     * Test 6: Cancelar evento.
     */
    @Test
    void shouldCancelEvent() {
        // Arrange
        Event event = createValidEvent();
        event.publish();
        
        // Act
        event.cancel();
        
        // Assert
        assertEquals(EventStatus.CANCELLED, event.getStatus());
    }
    
    /**
     * Test 7: No se puede cancelar evento ya cancelado.
     */
    @Test
    void shouldFailWhenCancellingAlreadyCancelledEvent() {
        // Arrange
        Event event = createValidEvent();
        event.cancel(); // Primera cancelación (OK)
        
        // Act & Assert
        assertThrows(IllegalStateException.class, () -> {
            event.cancel(); // Segunda cancelación (FALLA)
        });
    }
    
    // Método helper para crear eventos válidos en los tests
    private Event createValidEvent() {
        return Event.create(
            "Evento Test",
            "Descripción test",
            EventType.CONCERT,
            EventId.generate(),
            LocalDateTime.now().plusDays(30),
            new Location("Venue Test", "Ciudad Test", "Pais Test"),
            new Capacity(1000),
            Price.usd(50.00)
        );
    }
}
