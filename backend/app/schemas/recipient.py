from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class RecipientBase(BaseModel):
    """Base recipient schema."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personalization_data: Optional[Dict[str, Any]] = None


class RecipientCreate(RecipientBase):
    """Schema for creating a recipient."""
    campaign_id: int


class RecipientBulkCreate(BaseModel):
    """Schema for bulk creating recipients."""
    campaign_id: int
    recipients: list[RecipientBase]


class RecipientResponse(RecipientBase):
    """Schema for recipient response."""
    id: int
    campaign_id: int
    is_sent: bool
    is_failed: bool
    error_message: Optional[str] = None
    ab_variant: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
