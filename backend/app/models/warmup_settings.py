from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class WarmupSettings(Base):
    """Warmup settings model for email sending warm-up."""
    
    __tablename__ = "warmup_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Warmup configuration
    is_enabled = Column(Boolean, default=True)
    current_day = Column(Integer, default=1)
    start_volume = Column(Integer, default=20)
    growth_rate = Column(Float, default=2.0)  # Multiplier per day
    max_days = Column(Integer, default=14)
    
    # Current limits
    current_daily_limit = Column(Integer, default=20)
    emails_sent_today = Column(Integer, default=0)
    
    # Performance tracking
    bounce_rate = Column(Float, default=0.0)
    spam_rate = Column(Float, default=0.0)
    
    # Timestamps
    warmup_started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_reset_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<WarmupSettings Day {self.current_day} - Limit {self.current_daily_limit}>"
