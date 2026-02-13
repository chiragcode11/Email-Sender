from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.sql import func
from app.database import Base


class ABTest(Base):
    """A/B test model for testing different email variants."""
    
    __tablename__ = "ab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Test details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Variant A
    subject_a = Column(String, nullable=False)
    content_a = Column(Text, nullable=True)
    
    # Variant B
    subject_b = Column(String, nullable=False)
    content_b = Column(Text, nullable=True)
    
    # Split percentage (e.g., 50 means 50% A, 50% B)
    split_percentage = Column(Integer, default=50)
    
    # Results
    sent_a = Column(Integer, default=0)
    sent_b = Column(Integer, default=0)
    opens_a = Column(Integer, default=0)
    opens_b = Column(Integer, default=0)
    clicks_a = Column(Integer, default=0)
    clicks_b = Column(Integer, default=0)
    
    # Calculated rates
    open_rate_a = Column(Float, default=0.0)
    open_rate_b = Column(Float, default=0.0)
    click_rate_a = Column(Float, default=0.0)
    click_rate_b = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ABTest {self.name}>"
