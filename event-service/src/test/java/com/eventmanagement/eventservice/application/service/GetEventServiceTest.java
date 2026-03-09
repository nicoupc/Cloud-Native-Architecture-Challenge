package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.exception.EventNotFoundException;
import com.eventmanagement.eventservice.domain.model.*;
import com.eventmanagement.eventservice.infrastructure.InMemoryEventRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class GetEventServiceTest {

    private InMemoryEventRepository eventRepository;
    private GetEventService getEventService;

    @BeforeEach
    void setUp() {
        eventRepository = new InMemoryEventRepository();
        getEventService = new GetEventService(eventRepository);
    }

    @Test
    void shouldGetEventById() {
        Event event = createDraftEvent();
        eventRepository.save(event);

        Event result = getEventService.getById(event.getId());

        assertEquals(event.getId(), result.getId());
        assertEquals(event.getName(), result.getName());
    }

    @Test
    void shouldThrowWhenEventNotFound() {
        EventId nonExistentId = EventId.generate();

        assertThrows(EventNotFoundException.class,
            () -> getEventService.getById(nonExistentId));
    }

    @Test
    void shouldGetAllEvents() {
        Event event1 = createDraftEvent();
        Event event2 = createDraftEvent();
        eventRepository.save(event1);
        eventRepository.save(event2);

        List<Event> results = getEventService.getAll();

        assertEquals(2, results.size());
    }

    @Test
    void shouldReturnEmptyListWhenNoEvents() {
        List<Event> results = getEventService.getAll();

        assertTrue(results.isEmpty());
    }

    private Event createDraftEvent() {
        return Event.create(
            "Test Event",
            "Description",
            EventType.CONCERT,
            EventId.generate(),
            LocalDateTime.now().plusDays(30),
            new Location("Venue", "City", "Country"),
            new Capacity(1000),
            Price.usd(50.00)
        );
    }
}