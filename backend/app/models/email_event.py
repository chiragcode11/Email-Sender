from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class EventType(str, enum.Enum):
    """Email event type enum."""
    OPEN = "open"
    CLICK = "click"
    BOUNCE = "bounce"
    SPAM = "spam"
    UNSUBSCRIBE = "unsubscribe"


class EmailEvent(Base):
    """Email event model for tracking opens, clicks, etc."""
    
    __tablename__ = "email_events"
    
    id = Column(Integer, primary_key=True, index=True)
    email_log_id = Column(Integer, ForeignKey("email_logs.id"), nullable=False)
    
    # Event details
    event_type = Column(Enum(EventType), nullable=False, index=True)
    
    # Click tracking
    clicked_url = Column(String, nullable=True)
    
    # User agent and IP
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    # Location data (optional)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    email_log = relationship("EmailLog", back_populates="events")
    
    def __repr__(self):
        return f"<EmailEvent {self.event_type}>"
