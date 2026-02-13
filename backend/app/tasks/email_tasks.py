from celery import shared_task
from sqlalchemy import select
from datetime import datetime
import uuid

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.campaign import Campaign, CampaignStatus
from app.models.recipient import Recipient
from app.models.email_log import EmailLog, EmailStatus
from app.models.email_event import EmailEvent, EventType
from app.models.warmup_settings import WarmupSettings
from app.services.email_service import email_service
from app.services.warmup_service import warmup_service


@celery_app.task(name="app.tasks.email_tasks.send_campaign_emails")
def send_campaign_emails(campaign_id: int):
    """
    Send all emails for a campaign.
    This is a Celery task that runs asynchronously.
    """
    import asyncio
    import asyncio
    asyncio.run(send_campaign_emails_async(campaign_id))


async def send_campaign_emails_async(campaign_id: int):
    """Async implementation of send_campaign_emails."""
    print(f"DEBUG: Starting sending for campaign {campaign_id}")
    try:
        async with AsyncSessionLocal() as db:
            print(f"DEBUG: Database session created for campaign {campaign_id}")
            # Get campaign
            result = await db.execute(
                select(Campaign).where(Campaign.id == campaign_id)
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                print(f"DEBUG: Campaign {campaign_id} not found in database")
                return
            
            print(f"DEBUG: Found campaign {campaign.id}, updating status to SENDING")
            
            # Update campaign status
            campaign.status = CampaignStatus.SENDING
            campaign.started_at = datetime.utcnow()
            await db.commit()
            print(f"DEBUG: Campaign status updated to SENDING")
        
            # Get recipients
            result = await db.execute(
                select(Recipient).where(
                    Recipient.campaign_id == campaign_id,
                    Recipient.is_sent == False
                )
            )
            recipients = result.scalars().all()
            
            # Check warmup limits
            if campaign.use_warmup:
                warmup_check = await warmup_service.check_can_send(
                    campaign.user_id,
                    db,
                    len(recipients)
                )
                
                if not warmup_check["can_send"]:
                    # Limit recipients to remaining quota
                    recipients = recipients[:warmup_check["remaining"]]
            
            
            # Send emails
            sent_count = 0
            failed_count = 0
            
            for recipient in recipients:
                # Check for cancellation
                # We need to refresh campaign status from DB to see if it was cancelled
                await db.refresh(campaign)
                if campaign.status == CampaignStatus.CANCELLED:
                    print(f"DEBUG: Campaign {campaign_id} was cancelled by user. Stopping sending loop.")
                    break

                # Generate tracking ID
                tracking_id = str(uuid.uuid4())
                
                # Personalize content
                html_content = email_service.personalize_content(
                    campaign.html_content,
                    recipient.personalization_data or {}
                )
                
                print(f"DEBUG: Sending to recipient {recipient.email}...")
                # Send email
                try:
                    result = await email_service.send_email(
                        to_email=recipient.email,
                        subject=campaign.subject,
                        html_content=html_content,
                        plain_text=campaign.plain_text_content,
                        from_name=campaign.from_name,
                        reply_to=campaign.reply_to,
                        tracking_id=tracking_id,
                        track_opens=campaign.track_opens,
                        track_clicks=campaign.track_clicks
                    )
                    print(f"DEBUG: Send result for {recipient.email}: {result}")
                except Exception as e:
                    print(f"DEBUG: Exception sending to {recipient.email}: {e}")
                    result = {"success": False, "error": str(e)}
                
                # Create email log
                email_log = EmailLog(
                    campaign_id=campaign_id,
                    recipient_id=recipient.id,
                    to_email=recipient.email,
                    subject=campaign.subject,
                    from_email=campaign.from_email,
                    tracking_id=tracking_id,
                    message_id=result.get("message_id"),
                    status=EmailStatus.SENT if result["success"] else EmailStatus.FAILED,
                    error_message=result.get("error"),
                    sent_at=datetime.utcnow() if result["success"] else None
                )
                db.add(email_log)
                
                # Update recipient
                recipient.is_sent = result["success"]
                recipient.is_failed = not result["success"]
                recipient.error_message = result.get("error")
                recipient.sent_at = datetime.utcnow() if result["success"] else None
                
                if result["success"]:
                    sent_count += 1
                else:
                    failed_count += 1
                
                await db.commit()
            
            print(f"DEBUG: Finished sending loop. Sent: {sent_count}, Failed: {failed_count}")

            # Update campaign
            campaign.sent_count += sent_count
            campaign.failed_count += failed_count
            
            # Check if campaign is complete
            result = await db.execute(
                select(Recipient).where(
                    Recipient.campaign_id == campaign_id,
                    Recipient.is_sent == False,
                    Recipient.is_failed == False
                )
            )
            remaining = result.scalars().all()
            
            if not remaining:
                campaign.status = CampaignStatus.COMPLETED
                campaign.completed_at = datetime.utcnow()
                print(f"DEBUG: All recipients processed. Campaign marked as COMPLETED.")
            
            await db.commit()
            
            # Update warmup metrics
            if campaign.use_warmup:
                await warmup_service.record_sent_emails(
                    campaign.user_id,
                    sent_count,
                    db
                )
    except Exception as e:
        print(f"DEBUG: CRITICAL ERROR in send_campaign_emails_async: {e}")
        import traceback
        traceback.print_exc()
        
        # Update campaign status to FAILED on critical error
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Campaign).where(Campaign.id == campaign_id)
                )
                campaign = result.scalar_one_or_none()
                if campaign:
                    campaign.status = CampaignStatus.FAILED
                    await db.commit()
                    print(f"DEBUG: Campaign {campaign_id} status updated to FAILED due to critical error")
        except Exception as db_error:
            print(f"DEBUG: Failed to update campaign status to FAILED: {db_error}")


@celery_app.task(name="app.tasks.email_tasks.check_scheduled_campaigns")
def check_scheduled_campaigns():
    """Check for campaigns that should be sent now."""
    import asyncio
    asyncio.run(_check_scheduled_campaigns_async())


async def _check_scheduled_campaigns_async():
    """Async implementation of check_scheduled_campaigns."""
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        
        # Find scheduled campaigns that should be sent
        result = await db.execute(
            select(Campaign).where(
                Campaign.status == CampaignStatus.SCHEDULED,
                Campaign.scheduled_at <= now
            )
        )
        campaigns = result.scalars().all()
        
        # Trigger send for each campaign
        for campaign in campaigns:
            send_campaign_emails.delay(campaign.id)


@celery_app.task(name="app.tasks.email_tasks.update_warmup_limits")
def update_warmup_limits():
    """Update warmup limits for all users (runs daily)."""
    import asyncio
    asyncio.run(_update_warmup_limits_async())


async def _update_warmup_limits_async():
    """Async implementation of update_warmup_limits."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(WarmupSettings).where(WarmupSettings.is_enabled == True)
        )
        settings_list = result.scalars().all()
        
        for settings in settings_list:
            await warmup_service.update_warmup_progress(settings.user_id, db)
