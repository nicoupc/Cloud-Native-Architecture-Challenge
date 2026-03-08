package com.eventmanagement.eventservice.infrastructure;

import com.eventmanagement.eventservice.domain.model.Event;
import com.eventmanagement.eventservice.domain.model.EventId;
import com.eventmanagement.eventservice.domain.port.EventRepository;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class InMemoryEventRepository implements EventRepository {
    
    private final Map<EventId, Event> events = new HashMap<>();
    
    @Override
    public Event save(Event event) {
        events.put(event.getId(), event);
        return event;
    }
    
    @Override
    public Optional<Event> findById(EventId id) {
        return Optional.ofNullable(events.get(id));
    }
    
    @Override
    public List<Event> findAll() {
        return new ArrayList<>(events.values());
    }
    
    public void clear() {
        events.clear();
    }
    
    public int count() {
        return events.size();
    }
}
