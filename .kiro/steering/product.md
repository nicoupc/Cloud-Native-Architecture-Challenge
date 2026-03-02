# Product Overview

Cloud-native event management platform demonstrating multiple architectural patterns in a distributed system. The system handles event creation, ticket booking, payment processing, and notifications.

## Core Functionality

- Event creation and management (concerts, conferences, sports)
- Ticket booking and reservation system
- Distributed payment processing with compensation
- Asynchronous notification delivery

## Business Flows

1. **Event Creation**: Admins create events, system publishes availability
2. **Ticket Booking**: Users reserve tickets, system processes payment, confirms booking
3. **Payment Processing**: Orchestrated saga with automatic rollback on failure
4. **Notifications**: Buffered email confirmations and event reminders

## Educational Purpose

This is a learning project designed to demonstrate practical implementation of:
- Hexagonal Architecture (Ports & Adapters)
- CQRS (Command Query Responsibility Segregation)
- Event-Driven Architecture
- Saga Pattern with orchestration
- Buffer Pattern with SQS

Each microservice showcases different architectural patterns in real-world contexts.
