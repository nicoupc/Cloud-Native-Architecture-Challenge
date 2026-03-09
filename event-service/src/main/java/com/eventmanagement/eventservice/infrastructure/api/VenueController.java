package com.eventmanagement.eventservice.infrastructure.api;

import com.eventmanagement.eventservice.application.service.CreateVenueService;
import com.eventmanagement.eventservice.application.service.GetVenueService;
import com.eventmanagement.eventservice.domain.model.Venue;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/venues")
public class VenueController {
    
    private final CreateVenueService createVenueService;
    private final GetVenueService getVenueService;
    
    public VenueController(CreateVenueService createVenueService, GetVenueService getVenueService) {
        this.createVenueService = createVenueService;
        this.getVenueService = getVenueService;
    }
    
    @PostMapping
    public ResponseEntity<VenueResponse> createVenue(@RequestBody CreateVenueRequest request) {
        Venue venue = createVenueService.execute(
            request.name(),
            request.address(),
            request.city(),
            request.country(),
            request.maxCapacity()
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(VenueResponse.from(venue));
    }
    
    @GetMapping
    public ResponseEntity<List<VenueResponse>> listVenues() {
        List<VenueResponse> venues = getVenueService.getAll().stream()
            .map(VenueResponse::from)
            .toList();
        return ResponseEntity.ok(venues);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<VenueResponse> getVenue(@PathVariable UUID id) {
        return getVenueService.getById(id)
            .map(venue -> ResponseEntity.ok(VenueResponse.from(venue)))
            .orElse(ResponseEntity.notFound().build());
    }
    
    record CreateVenueRequest(String name, String address, String city, String country, int maxCapacity) {}
    
    record VenueResponse(String id, String name, String address, String city, String country, int maxCapacity, String createdAt) {
        static VenueResponse from(Venue venue) {
            return new VenueResponse(
                venue.getId().value().toString(),
                venue.getName(),
                venue.getAddress(),
                venue.getCity(),
                venue.getCountry(),
                venue.getMaxCapacity(),
                venue.getCreatedAt().toString()
            );
        }
    }
}