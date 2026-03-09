"""
Ports (Interfaces) for Notification Service

Define contracts for external dependencies.
"""

from abc import ABC, abstractmethod

from .value_objects import EmailAddress, EmailSubject, EmailBody


class EmailProvider(ABC):
    """
    Port for email sending
    
    Implementations: MockEmailProvider, SESEmailProvider, etc.
    """
    
    @abstractmethod
    async def send_email(
        self,
        recipient: EmailAddress,
        subject: EmailSubject,
        body: EmailBody
    ) -> bool:
        """
        Send email to recipient
        
        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass



