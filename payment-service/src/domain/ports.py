"""
Domain Ports - Interfaces for external dependencies

Ports define WHAT the domain needs, not HOW it's implemented.
Infrastructure layer will provide the adapters (HOW).

This follows the Dependency Inversion Principle:
- Domain depends on abstractions (ports)
- Infrastructure depends on domain (implements ports)
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from .payment_saga import PaymentSaga
from .value_objects import SagaId, BookingId, Amount
from .events import DomainEvent


class SagaRepository(ABC):
    """
    Port: Saga Repository
    
    Defines persistence operations for sagas.
    Infrastructure will implement using DynamoDB.
    """
    
    @abstractmethod
    async def save(self, saga: PaymentSaga) -> PaymentSaga:
        """
        Save saga state
        
        Args:
            saga: Saga to persist
            
        Returns:
            Persisted saga
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, saga_id: SagaId) -> Optional[PaymentSaga]:
        """
        Find saga by ID
        
        Args:
            saga_id: Saga identifier
            
        Returns:
            Saga if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_booking_id(
        self,
        booking_id: BookingId
    ) -> Optional[PaymentSaga]:
        """
        Find saga by booking ID
        
        Args:
            booking_id: Booking identifier
            
        Returns:
            Saga if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_all(
        self,
        limit: int = 100,
        last_key: Optional[str] = None
    ) -> tuple[List[PaymentSaga], Optional[str]]:
        """
        Find all sagas with pagination
        
        Args:
            limit: Maximum number of sagas to return
            last_key: Pagination token
            
        Returns:
            Tuple of (sagas, next_page_token)
        """
        pass


class EventPublisher(ABC):
    """
    Port: Event Publisher
    
    Publishes domain events to external systems.
    Infrastructure will implement using EventBridge.
    """
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a single domain event
        
        Args:
            event: Domain event to publish
        """
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple domain events
        
        Args:
            events: List of domain events to publish
        """
        pass


class PaymentGateway(ABC):
    """
    Port: Payment Gateway
    
    Processes payments through external payment provider.
    Infrastructure will implement as mock for this project.
    
    In production: Stripe, PayPal, Adyen, etc.
    """
    
    @abstractmethod
    async def process_payment(
        self,
        booking_id: BookingId,
        amount: Amount
    ) -> dict:
        """
        Process a payment
        
        Args:
            booking_id: Booking identifier
            amount: Payment amount
            
        Returns:
            Payment result with payment_id and status
            
        Raises:
            PaymentGatewayError: If payment fails
        """
        pass
    
    @abstractmethod
    async def refund_payment(
        self,
        payment_id: str,
        amount: Amount
    ) -> dict:
        """
        Refund a payment (compensation)
        
        Args:
            payment_id: Payment identifier to refund
            amount: Refund amount
            
        Returns:
            Refund result
            
        Raises:
            PaymentGatewayError: If refund fails
        """
        pass


class BookingServiceClient(ABC):
    """
    Port: Booking Service Client
    
    Communicates with Booking Service via HTTP.
    Infrastructure will implement using httpx.
    """
    
    @abstractmethod
    async def confirm_booking(self, booking_id: BookingId) -> dict:
        """
        Confirm a booking
        
        Args:
            booking_id: Booking to confirm
            
        Returns:
            Confirmation result
            
        Raises:
            BookingServiceError: If confirmation fails
        """
        pass
    
    @abstractmethod
    async def cancel_booking(
        self,
        booking_id: BookingId,
        reason: str
    ) -> dict:
        """
        Cancel a booking (compensation)
        
        Args:
            booking_id: Booking to cancel
            reason: Cancellation reason
            
        Returns:
            Cancellation result
            
        Raises:
            BookingServiceError: If cancellation fails
        """
        pass
    
    @abstractmethod
    async def get_booking(self, booking_id: BookingId) -> dict:
        """
        Get booking details
        
        Args:
            booking_id: Booking identifier
            
        Returns:
            Booking details
            
        Raises:
            BookingServiceError: If booking not found
        """
        pass


class NotificationServiceClient(ABC):
    """
    Port: Notification Service Client
    
    Sends notifications to users.
    Infrastructure will implement using EventBridge/SQS.
    """
    
    @abstractmethod
    async def send_payment_confirmation(
        self,
        booking_id: BookingId,
        amount: Amount
    ) -> None:
        """
        Send payment confirmation notification
        
        Args:
            booking_id: Booking identifier
            amount: Payment amount
        """
        pass
    
    @abstractmethod
    async def send_payment_failure(
        self,
        booking_id: BookingId,
        reason: str
    ) -> None:
        """
        Send payment failure notification
        
        Args:
            booking_id: Booking identifier
            reason: Failure reason
        """
        pass


# Custom exceptions for ports
class PaymentGatewayError(Exception):
    """Raised when payment gateway operation fails"""
    pass


class BookingServiceError(Exception):
    """Raised when booking service operation fails"""
    pass


class NotificationServiceError(Exception):
    """Raised when notification service operation fails"""
    pass
