from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enum."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """Campaign model for email campaigns."""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Campaign details
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    from_name = Column(String, nullable=False)
    from_email = Column(String, nullable=False)
    reply_to = Column(String, nullable=True)
    
    # Content
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    html_content = Column(Text, nullable=True)
    plain_text_content = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_test_id = Column(Integer, ForeignKey("ab_tests.id"), nullable=True)
    
    # Settings
    use_warmup = Column(Boolean, default=True)
    track_opens = Column(Boolean, default=True)
    track_clicks = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recipients = relationship("Recipient", back_populates="campaign", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Campaign {self.name} ({self.status})>"
