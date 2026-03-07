"""
Mock Email Provider

Simulates email sending for testing and development.
"""

import logging
import asyncio
import random
from typing import List, Dict, Any
from datetime import datetime

from ...domain import EmailProvider, EmailAddress, EmailSubject, EmailBody

logger = logging.getLogger(__name__)


class MockEmailProvider(EmailProvider):
    """
    Mock implementation of EmailProvider
    
    Simulates email sending with configurable success rate and delay.
    Stores sent emails in memory for testing.
    """
    
    def __init__(self, success_rate: float = 0.9, delay_ms: int = 100):
        """
        Initialize mock provider
        
        Args:
            success_rate: Probability of successful send (0.0 to 1.0)
            delay_ms: Simulated network delay in milliseconds
        """
        self.success_rate = success_rate
        self.delay_ms = delay_ms
        self.sent_emails: List[Dict[str, Any]] = []
    
    async def send_email(
        self,
        recipient: EmailAddress,
        subject: EmailSubject,
        body: EmailBody
    ) -> bool:
        """
        Simulate sending email
        
        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body
            
        Returns:
            True if "sent" successfully, False otherwise
        """
        # Simulate network delay
        await asyncio.sleep(self.delay_ms / 1000.0)
        
        # Simulate random failures
        success = random.random() < self.success_rate
        
        if success:
            # Store sent email
            email_record = {
                "recipient": str(recipient),
                "subject": str(subject),
                "body": str(body),
                "sent_at": datetime.utcnow().isoformat()
            }
            self.sent_emails.append(email_record)
            
            logger.info(
                f"[MOCK] Email sent to {recipient}\n"
                f"Subject: {subject}\n"
                f"Body preview: {str(body)[:100]}..."
            )
        else:
            logger.warning(f"[MOCK] Failed to send email to {recipient}")
        
        return success
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all sent emails (for testing)"""
        return self.sent_emails.copy()
    
    def clear_sent_emails(self) -> None:
        """Clear sent emails history (for testing)"""
        self.sent_emails.clear()
