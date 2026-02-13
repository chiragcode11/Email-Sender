from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Recipient(Base):
    """Recipient model for campaign recipients."""
    
    __tablename__ = "recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    
    # Contact information
    email = Column(String, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Personalization data (JSON field for flexible data)
    personalization_data = Column(JSON, nullable=True)
    
    # Status
    is_sent = Column(Boolean, default=False)
    is_failed = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)
    
    # A/B Test variant
    ab_variant = Column(String, nullable=True)  # 'A', 'B', or None
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="recipients")
    email_logs = relationship("EmailLog", back_populates="recipient")
    
    def __repr__(self):
        return f"<Recipient {self.email}>"
