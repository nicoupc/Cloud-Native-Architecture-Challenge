package com.eventmanagement.eventservice.application.service;

import com.eventmanagement.eventservice.domain.event.EventCancelled;
import com.eventmanagement.eventservice.domain.exception.EventNotFoundException;
import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import com.eventmanagement.eventservice.domain.port.EventPublisher;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Use Case: Cancel an event.
 * Transitions event to CANCELLED and publishes EventCancelled to EventBridge.
 */
@Service
@Transactional
public class CancelEventService {
    
    private final EventRepository eventRepository;
    private final EventPublisher eventPublisher;
    
    public CancelEventService(
        EventRepository eventRepository,
        EventPublisher eventPublisher
    ) {
        this.eventRepository = eventRepository;
        this.eventPublisher = eventPublisher;
    }
    
    public Event execute(EventId eventId, String reason) {
        Event event = eventRepository.findById(eventId)
            .orElseThrow(() -> new EventNotFoundException(eventId));
        
        event.cancel();
        
        Event cancelledEvent = eventRepository.save(event);
        
        EventCancelled domainEvent = EventCancelled.from(cancelledEvent, reason);
        eventPublisher.publish(domainEvent);
        
        return cancelledEvent;
    }
}
