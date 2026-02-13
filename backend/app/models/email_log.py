from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class EmailStatus(str, enum.Enum):
    """Email delivery status enum."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    DELIVERED = "delivered"


class EmailLog(Base):
    """Email log model for tracking sent emails."""
    
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("recipients.id"), nullable=False)
    
    # Email details
    to_email = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    from_email = Column(String, nullable=False)
    
    # Status
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Tracking
    tracking_id = Column(String, unique=True, index=True, nullable=False)
    message_id = Column(String, nullable=True)  # SMTP message ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="email_logs")
    recipient = relationship("Recipient", back_populates="email_logs")
    events = relationship("EmailEvent", back_populates="email_log", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EmailLog {self.to_email} ({self.status})>"
