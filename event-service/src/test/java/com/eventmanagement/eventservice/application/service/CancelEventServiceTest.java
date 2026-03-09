package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.event.DomainEvent;
import com.eventmanagement.eventservice.domain.exception.EventNotFoundException;
import com.eventmanagement.eventservice.domain.model.*;
import com.eventmanagement.eventservice.domain.port.EventPublisher;
import com.eventmanagement.eventservice.infrastructure.InMemoryEventRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class CancelEventServiceTest {

    private InMemoryEventRepository eventRepository;
    private List<DomainEvent> publishedEvents;
    private CancelEventService cancelEventService;

    @BeforeEach
    void setUp() {
        eventRepository = new InMemoryEventRepository();
        publishedEvents = new ArrayList<>();
        EventPublisher eventPublisher = publishedEvents::add;
        cancelEventService = new CancelEventService(eventRepository, eventPublisher);
    }

    @Test
    void shouldCancelPublishedEvent() {
        Event event = createDraftEvent();
        event.publish();
        eventRepository.save(event);

        Event result = cancelEventService.execute(event.getId(), "Low ticket sales");

        assertEquals(EventStatus.CANCELLED, result.getStatus());
    }

    @Test
    void shouldCancelDraftEvent() {
        Event event = createDraftEvent();
        eventRepository.save(event);

        Event result = cancelEventService.execute(event.getId(), "Changed plans");

        assertEquals(EventStatus.CANCELLED, result.getStatus());
    }

    @Test
    void shouldThrowWhenEventNotFound() {
        EventId nonExistentId = EventId.generate();

        assertThrows(EventNotFoundException.class,
            () -> cancelEventService.execute(nonExistentId, "reason"));
    }

    @Test
    void shouldThrowWhenEventAlreadyCancelled() {
        Event event = createDraftEvent();
        event.cancel();
        eventRepository.save(event);

        assertThrows(IllegalStateException.class,
            () -> cancelEventService.execute(event.getId(), "Double cancel"));
    }

    @Test
    void shouldPublishEventCancelledDomainEvent() {
        Event event = createDraftEvent();
        eventRepository.save(event);

        cancelEventService.execute(event.getId(), "Weather issues");

        assertEquals(1, publishedEvents.size());
        assertEquals("EventCancelled", publishedEvents.get(0).eventType());
    }

    @Test
    void shouldPersistCancelledEvent() {
        Event event = createDraftEvent();
        event.publish();
        eventRepository.save(event);

        cancelEventService.execute(event.getId(), "Venue unavailable");

        Event saved = eventRepository.findById(event.getId()).orElseThrow();
        assertEquals(EventStatus.CANCELLED, saved.getStatus());
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