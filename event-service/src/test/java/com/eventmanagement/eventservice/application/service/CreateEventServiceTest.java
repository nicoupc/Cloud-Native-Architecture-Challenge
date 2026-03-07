package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.model.*;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import com.eventmanagement.eventservice.infrastructure.InMemoryEventRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.time.LocalDateTime;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Test del servicio CreateEventService.
 * 
 * Aquí probamos el FLUJO COMPLETO:
 * Application Layer → Domain Layer → Repository
 */
class CreateEventServiceTest {
    
    private EventRepository eventRepository;
    private CreateEventService createEventService;
    
    /**
     * @BeforeEach se ejecuta ANTES de cada test.
     * Aquí preparamos el entorno limpio.
     */
    @BeforeEach
    void setUp() {
        // Creamos un repositorio en memoria
        eventRepository = new InMemoryEventRepository();
        
        // Creamos el servicio con el repositorio
        createEventService = new CreateEventService(eventRepository);
    }
    
    /**
     * Test 1: Crear evento exitosamente.
     * Verifica que el evento se guarda en el repositorio.
     */
    @Test
    void shouldCreateAndSaveEvent() {
        // Arrange
        String name = "Concierto Coldplay";
        String description = "Concierto en vivo";
        EventType type = EventType.CONCERT;
        EventId venueId = EventId.generate();
        LocalDateTime eventDate = LocalDateTime.now().plusDays(30);
        Capacity capacity = new Capacity(5000);
        Price price = Price.usd(75.00);
        
        // Crear el evento usando el dominio
        Event event = Event.create(
            name, description, type, venueId, eventDate, capacity, price
        );
        
        // Act
        Event createdEvent = createEventService.execute(event);
        
        // Assert
        assertNotNull(createdEvent, "El evento creado no debe ser null");
        assertNotNull(createdEvent.getId(), "El evento debe tener un ID");
        assertEquals(EventStatus.DRAFT, createdEvent.getStatus(), "Debe estar en DRAFT");
        
        // Verificar que se guardó en el repositorio
        Event savedEvent = eventRepository.findById(createdEvent.getId())
            .orElseThrow(() -> new AssertionError("El evento no se guardó en el repositorio"));
        
        assertEquals(createdEvent.getId(), savedEvent.getId());
        assertEquals(name, savedEvent.getName());
    }
    
    /**
     * Test 2: Falla cuando la fecha es pasada.
     * El dominio debe lanzar excepción.
     */
    @Test
    void shouldFailWhenEventDateIsInPast() {
        // Arrange
        LocalDateTime pastDate = LocalDateTime.now().minusDays(1);
        
        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            Event.create(
                "Evento Pasado",
                "Descripción",
                EventType.CONCERT,
                EventId.generate(),
                pastDate, // ← Fecha inválida
                new Capacity(100),
                Price.usd(50.00)
            );
        });
    }
    
    /**
     * Test 3: Múltiples eventos se guardan independientemente.
     */
    @Test
    void shouldCreateMultipleEventsIndependently() {
        // Arrange
        EventId venue1 = EventId.generate();
        EventId venue2 = EventId.generate();
        LocalDateTime futureDate = LocalDateTime.now().plusDays(30);
        
        // Crear eventos usando el dominio
        Event event1 = Event.create(
            "Concierto A", "Desc A", EventType.CONCERT,
            venue1, futureDate, new Capacity(1000), Price.usd(50.00)
        );
        
        Event event2 = Event.create(
            "Concierto B", "Desc B", EventType.CONFERENCE,
            venue2, futureDate, new Capacity(2000), Price.usd(100.00)
        );
        
        // Act
        Event savedEvent1 = createEventService.execute(event1);
        Event savedEvent2 = createEventService.execute(event2);
        
        // Assert
        assertNotEquals(savedEvent1.getId(), savedEvent2.getId(), "Deben tener IDs diferentes");
        
        // Ambos deben estar guardados
        assertTrue(eventRepository.findById(savedEvent1.getId()).isPresent());
        assertTrue(eventRepository.findById(savedEvent2.getId()).isPresent());
    }
}
