"""
Mock Payment Gateway - Simulated payment processor

Implements PaymentGateway port with mock behavior.
In production: Replace with Stripe, PayPal, Adyen, etc.
"""

import random
import uuid
from typing import Dict

from ...domain.ports import PaymentGateway, PaymentGatewayError
from ...domain.value_objects import BookingId, Amount


class MockPaymentGateway(PaymentGateway):
    """
    Mock payment gateway for testing and development
    
    Simulates payment processing with configurable success rate.
    """
    
    def __init__(self, success_rate: float = 0.8):
        """
        Initialize mock gateway
        
        Args:
            success_rate: Probability of successful payment (0.0-1.0)
        """
        self.success_rate = success_rate
        self.processed_payments: Dict[str, dict] = {}
    
    async def process_payment(
        self,
        booking_id: BookingId,
        amount: Amount
    ) -> dict:
        """
        Process a payment (simulated)
        
        Args:
            booking_id: Booking identifier
            amount: Payment amount
            
        Returns:
            Payment result with payment_id and status
            
        Raises:
            PaymentGatewayError: If payment fails (randomly based on success_rate)
        """
        # Simulate processing delay
        # In production: This would be an HTTP call to payment provider
        
        # Random success/failure based on success_rate
        if random.random() > self.success_rate:
            raise PaymentGatewayError(
                f"Payment declined for booking {booking_id.value}. "
                "Insufficient funds or card declined."
            )
        
        # Generate payment ID
        payment_id = str(uuid.uuid4())
        
        # Store payment record
        payment_record = {
            "payment_id": payment_id,
            "booking_id": booking_id.value,
            "amount": amount.value,
            "currency": amount.currency,
            "status": "COMPLETED",
            "provider": "MOCK_GATEWAY"
        }
        
        self.processed_payments[payment_id] = payment_record
        
        return payment_record
    
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
        # Check if payment exists
        if payment_id not in self.processed_payments:
            raise PaymentGatewayError(
                f"Payment {payment_id} not found. Cannot refund."
            )
        
        payment = self.processed_payments[payment_id]
        
        # Validate refund amount
        if amount.value > payment["amount"]:
            raise PaymentGatewayError(
                f"Refund amount {amount.value} exceeds payment amount {payment['amount']}"
            )
        
        # Generate refund ID
        refund_id = str(uuid.uuid4())
        
        # Update payment status
        payment["status"] = "REFUNDED"
        payment["refund_id"] = refund_id
        
        return {
            "refund_id": refund_id,
            "payment_id": payment_id,
            "amount": amount.value,
            "currency": amount.currency,
            "status": "COMPLETED"
        }
    
    def get_payment(self, payment_id: str) -> dict:
        """
        Get payment details (helper for testing)
        
        Args:
            payment_id: Payment identifier
            
        Returns:
            Payment record
        """
        return self.processed_payments.get(payment_id)
