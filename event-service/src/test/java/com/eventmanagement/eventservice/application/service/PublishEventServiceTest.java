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

class PublishEventServiceTest {

    private InMemoryEventRepository eventRepository;
    private List<DomainEvent> publishedEvents;
    private PublishEventService publishEventService;

    @BeforeEach
    void setUp() {
        eventRepository = new InMemoryEventRepository();
        publishedEvents = new ArrayList<>();
        EventPublisher eventPublisher = publishedEvents::add;
        publishEventService = new PublishEventService(eventRepository, eventPublisher);
    }

    @Test
    void shouldPublishDraftEvent() {
        Event event = createDraftEvent();
        eventRepository.save(event);

        Event result = publishEventService.execute(event.getId());

        assertEquals(EventStatus.PUBLISHED, result.getStatus());
    }

    @Test
    void shouldThrowWhenEventNotFound() {
        EventId nonExistentId = EventId.generate();

        assertThrows(EventNotFoundException.class,
            () -> publishEventService.execute(nonExistentId));
    }

    @Test
    void shouldThrowWhenEventAlreadyPublished() {
        Event event = createDraftEvent();
        event.publish();
        eventRepository.save(event);

        assertThrows(IllegalStateException.class,
            () -> publishEventService.execute(event.getId()));
    }

    @Test
    void shouldThrowWhenEventIsCancelled() {
        Event event = createDraftEvent();
        event.cancel();
        eventRepository.save(event);

        assertThrows(IllegalStateException.class,
            () -> publishEventService.execute(event.getId()));
    }

    @Test
    void shouldPersistPublishedEvent() {
        Event event = createDraftEvent();
        eventRepository.save(event);

        publishEventService.execute(event.getId());

        Event saved = eventRepository.findById(event.getId()).orElseThrow();
        assertEquals(EventStatus.PUBLISHED, saved.getStatus());
    }

    @Test
    void shouldPublishEventPublishedDomainEvent() {
        Event event = createDraftEvent();
        eventRepository.save(event);

        publishEventService.execute(event.getId());

        assertEquals(1, publishedEvents.size());
        assertEquals("EventPublished", publishedEvents.get(0).eventType());
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