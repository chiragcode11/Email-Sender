from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.campaign import Campaign
from app.models.recipient import Recipient
from app.models.email_log import EmailLog
from app.models.email_event import EmailEvent, EventType
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate, CampaignStats
from app.schemas.recipient import RecipientCreate, RecipientBulkCreate, RecipientResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign."""
    new_campaign = Campaign(
        user_id=current_user.id,
        **campaign_data.model_dump()
    )
    
    db.add(new_campaign)
    await db.commit()
    await db.refresh(new_campaign)
    
    return new_campaign


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all campaigns for the current user."""
    result = await db.execute(
        select(Campaign).where(Campaign.user_id == current_user.id).order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific campaign."""
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a campaign."""
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update fields
    for field, value in campaign_data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a campaign."""
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    await db.delete(campaign)
    await db.commit()


@router.post("/{campaign_id}/recipients", status_code=status.HTTP_201_CREATED)
async def add_recipients(
    campaign_id: int,
    recipient_data: RecipientBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add recipients to a campaign."""
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Create recipients
    recipients = []
    for recipient in recipient_data.recipients:
        new_recipient = Recipient(
            campaign_id=campaign_id,
            **recipient.model_dump()
        )
        recipients.append(new_recipient)
        db.add(new_recipient)
    
    # Update campaign total recipients count
    campaign.total_recipients += len(recipients)
    
    await db.commit()
    
    return {"message": f"Added {len(recipients)} recipients", "count": len(recipients)}


@router.get("/{campaign_id}/recipients", response_model=List[RecipientResponse])
async def list_recipients(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all recipients for a campaign."""
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get recipients
    result = await db.execute(
        select(Recipient).where(Recipient.campaign_id == campaign_id)
    )
    recipients = result.scalars().all()
    
    return recipients


@router.delete("/{campaign_id}/recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(
    campaign_id: int,
    recipient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a recipient from a campaign."""
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get recipient
    result = await db.execute(
        select(Recipient).where(
            Recipient.id == recipient_id,
            Recipient.campaign_id == campaign_id
        )
    )
    recipient = result.scalar_one_or_none()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    await db.delete(recipient)
    
    # Update campaign total recipients count
    if campaign.total_recipients > 0:
        campaign.total_recipients -= 1
        
    await db.commit()


from fastapi import BackgroundTasks

@router.post("/{campaign_id}/send", status_code=status.HTTP_200_OK)
async def send_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger sending of a campaign."""
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    from app.tasks.email_tasks import send_campaign_emails_async
    background_tasks.add_task(send_campaign_emails_async, campaign_id)
    
    return {"message": "Campaign sending started"}


@router.post("/{campaign_id}/retry", status_code=status.HTTP_200_OK)
async def retry_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retry a failed or cancelled campaign.
    This will resume sending to recipients who haven't received the email yet.
    """
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if campaign can be retried
    from app.models.campaign import CampaignStatus
    if campaign.status not in [CampaignStatus.FAILED, CampaignStatus.CANCELLED, CampaignStatus.COMPLETED]:
        # We allow retrying COMPLETED if there were failures (failed_count > 0)
        # But generally we just want to reset status to SENDING if it's not already sending
        if campaign.status == CampaignStatus.SENDING:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign is already sending"
            )
    
    # Update status to sending
    campaign.status = CampaignStatus.SENDING
    await db.commit()
    
    # Trigger sending task
    from app.tasks.email_tasks import send_campaign_emails_async
    background_tasks.add_task(send_campaign_emails_async, campaign_id)
    
    return {"message": "Campaign retry started"}


@router.get("/{campaign_id}/stats", response_model=CampaignStats)
async def get_campaign_stats(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get campaign statistics."""
    # Verify campaign ownership
    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.user_id == current_user.id
        )
    )
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get total sent
    total_sent = campaign.sent_count
    
    # Get event counts
    opens_result = await db.execute(
        select(func.count(EmailEvent.id))
        .join(EmailLog)
        .where(
            EmailLog.campaign_id == campaign_id,
            EmailEvent.event_type == EventType.OPEN
        )
    )
    total_opens = opens_result.scalar() or 0
    
    clicks_result = await db.execute(
        select(func.count(EmailEvent.id))
        .join(EmailLog)
        .where(
            EmailLog.campaign_id == campaign_id,
            EmailEvent.event_type == EventType.CLICK
        )
    )
    total_clicks = clicks_result.scalar() or 0
    
    bounces_result = await db.execute(
        select(func.count(EmailEvent.id))
        .join(EmailLog)
        .where(
            EmailLog.campaign_id == campaign_id,
            EmailEvent.event_type == EventType.BOUNCE
        )
    )
    total_bounces = bounces_result.scalar() or 0
    
    # Calculate rates
    open_rate = (total_opens / total_sent * 100) if total_sent > 0 else 0
    click_rate = (total_clicks / total_sent * 100) if total_sent > 0 else 0
    bounce_rate = (total_bounces / total_sent * 100) if total_sent > 0 else 0
    
    return CampaignStats(
        campaign_id=campaign_id,
        total_sent=total_sent,
        total_opens=total_opens,
        total_clicks=total_clicks,
        total_bounces=total_bounces,
        open_rate=round(open_rate, 2),
        click_rate=round(click_rate, 2),
        bounce_rate=round(bounce_rate, 2)
    )
