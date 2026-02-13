from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class EmailTemplate(Base):
    """Email template model."""
    
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Template details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Content
    html_content = Column(Text, nullable=False)
    plain_text_content = Column(Text, nullable=True)
    
    # Variables used in template
    variables = Column(JSON, nullable=True)  # List of variable names like ["first_name", "company"]
    
    # Preview
    thumbnail_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EmailTemplate {self.name}>"
