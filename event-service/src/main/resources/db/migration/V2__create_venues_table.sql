-- Flyway Migration V2: Create venues table
-- Implements the Venue aggregate from DDD (challenge.md line 54)

CREATE TABLE venues (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    max_capacity INTEGER NOT NULL CHECK (max_capacity > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_venue_city ON venues(city);
CREATE INDEX idx_venue_country ON venues(country);

-- Add location columns to events table (were added by Hibernate but not in migration)
ALTER TABLE events ADD COLUMN IF NOT EXISTS location_venue VARCHAR(200) NOT NULL DEFAULT 'TBD';
ALTER TABLE events ADD COLUMN IF NOT EXISTS location_city VARCHAR(100) NOT NULL DEFAULT 'TBD';
ALTER TABLE events ADD COLUMN IF NOT EXISTS location_country VARCHAR(100) NOT NULL DEFAULT 'TBD';

COMMENT ON TABLE venues IS 'Venues where events take place';