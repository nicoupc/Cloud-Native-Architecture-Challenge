"""
Payment Service - Main Application

FastAPI application with dependency injection for Saga Pattern.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .application.saga_orchestrator import SagaOrchestrator
from .infrastructure.persistence.dynamodb_saga_repository import DynamoDBSagaRepository
from .infrastructure.messaging.eventbridge_publisher import EventBridgePublisher
from .infrastructure.gateway.mock_payment_gateway import MockPaymentGateway
from .infrastructure.clients.booking_service_client import HttpBookingServiceClient
from .infrastructure.clients.notification_service_client import EventBridgeNotificationClient
from .infrastructure.api.saga_controller import router as saga_router, get_orchestrator as controller_get_orchestrator


# Global orchestrator instance (simple DI)
_orchestrator: SagaOrchestrator = None


def get_orchestrator() -> SagaOrchestrator:
    """Dependency injection for SagaOrchestrator"""
    return _orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    
    Initializes dependencies on startup and cleans up on shutdown.
    """
    global _orchestrator
    
    # Initialize all adapters
    saga_repository = DynamoDBSagaRepository()
    event_publisher = EventBridgePublisher()
    payment_gateway = MockPaymentGateway(success_rate=0.8)
    booking_client = HttpBookingServiceClient()
    notification_client = EventBridgeNotificationClient()
    
    # Create orchestrator with all dependencies
    _orchestrator = SagaOrchestrator(
        saga_repository=saga_repository,
        event_publisher=event_publisher,
        payment_gateway=payment_gateway,
        booking_service=booking_client,
        notification_service=notification_client
    )
    
    print("✅ Payment Service started successfully")
    print(f"📊 DynamoDB Table: {saga_repository.table_name}")
    print(f"📡 EventBridge Bus: {event_publisher.event_bus_name}")
    print(f"💳 Payment Gateway: Mock (success rate: 80%)")
    
    yield
    
    # Cleanup (if needed)
    print("🛑 Payment Service shutting down")


# Create FastAPI application
app = FastAPI(
    title="Payment Service",
    description="Saga Pattern implementation for distributed payment processing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Override dependency in the app (not the router)
app.dependency_overrides[controller_get_orchestrator] = get_orchestrator

# Register routers
app.include_router(saga_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "payment-service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Payment Service",
        "description": "Saga Pattern for distributed transactions",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "3002"))
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
