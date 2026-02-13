from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmailTemplateBase(BaseModel):
    """Base email template schema."""
    name: str
    description: Optional[str] = None
    html_content: str
    plain_text_content: Optional[str] = None
    variables: Optional[List[str]] = None


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating an email template."""
    pass


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template."""
    name: Optional[str] = None
    description: Optional[str] = None
    html_content: Optional[str] = None
    plain_text_content: Optional[str] = None
    variables: Optional[List[str]] = None


class EmailTemplateResponse(EmailTemplateBase):
    """Schema for email template response."""
    id: int
    user_id: int
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
