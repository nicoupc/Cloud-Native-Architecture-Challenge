-- Flyway Migration V1: Crear tabla events
-- 
-- Flyway ejecuta este script automáticamente al iniciar la aplicación.
-- Solo se ejecuta UNA VEZ (Flyway guarda un registro de qué migraciones ya corrieron).

CREATE TABLE events (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    venue_id UUID NOT NULL,
    event_date TIMESTAMP NOT NULL,
    total_capacity INTEGER NOT NULL CHECK (total_capacity >= 0),
    available_capacity INTEGER NOT NULL CHECK (available_capacity >= 0),
    price_amount DECIMAL(10, 2) NOT NULL CHECK (price_amount >= 0),
    price_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas
CREATE INDEX idx_event_status ON events(status);
CREATE INDEX idx_event_date ON events(event_date);
CREATE INDEX idx_event_type ON events(type);

-- Comentarios para documentación
COMMENT ON TABLE events IS 'Tabla de eventos (conciertos, conferencias, deportes)';
COMMENT ON COLUMN events.venue_id IS 'ID del venue donde se realiza el evento';
COMMENT ON COLUMN events.available_capacity IS 'Capacidad disponible (disminuye con reservas)';
