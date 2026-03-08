package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.exception.EventNotFoundException;
import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import com.eventmanagement.eventservice.domain.port.EventRepository;

import java.util.List;

/**
 * Use Case: Query events.
 * Retrieves events by ID or lists all events.
 */
public class GetEventService {
    
    private final EventRepository eventRepository;
    
    public GetEventService(EventRepository eventRepository) {
        this.eventRepository = eventRepository;
    }
    
    public Event getById(EventId eventId) {
        return eventRepository.findById(eventId)
            .orElseThrow(() -> new EventNotFoundException(eventId));
    }
    
    public List<Event> getAll() {
        return eventRepository.findAll();
    }
}
