from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.campaign import CampaignStatus


class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str
    subject: str
    from_name: str
    from_email: EmailStr
    reply_to: Optional[EmailStr] = None


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""
    template_id: Optional[int] = None
    html_content: Optional[str] = None
    plain_text_content: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    use_warmup: bool = True
    track_opens: bool = True
    track_clicks: bool = True


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    name: Optional[str] = None
    subject: Optional[str] = None
    from_name: Optional[str] = None
    from_email: Optional[EmailStr] = None
    reply_to: Optional[EmailStr] = None
    html_content: Optional[str] = None
    plain_text_content: Optional[str] = None
    status: Optional[CampaignStatus] = None
    scheduled_at: Optional[datetime] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign response."""
    id: int
    user_id: int
    status: CampaignStatus
    template_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_recipients: int
    sent_count: int
    failed_count: int
    is_ab_test: bool
    use_warmup: bool
    track_opens: bool
    track_clicks: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    """Schema for campaign statistics."""
    campaign_id: int
    total_sent: int
    total_opens: int
    total_clicks: int
    total_bounces: int
    open_rate: float
    click_rate: float
    bounce_rate: float
