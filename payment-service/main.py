"""
Payment Service - Main Entry Point

Saga Pattern implementation for distributed payment processing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Payment Service",
    description="Saga Pattern implementation for distributed transactions",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "payment-service",
        "version": "0.1.0",
        "status": "running",
        "pattern": "Saga Pattern (Orchestration)",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "payment-service",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3002,
        reload=True,
        log_level="info",
    )
