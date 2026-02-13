from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models.email_log import EmailLog
from app.models.email_event import EmailEvent, EventType

router = APIRouter(prefix="/track", tags=["Tracking"])


@router.get("/open/{tracking_id}")
async def track_open(
    tracking_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Track email open event."""
    # Find email log
    result = await db.execute(
        select(EmailLog).where(EmailLog.tracking_id == tracking_id)
    )
    email_log = result.scalar_one_or_none()
    
    if email_log:
        # Check if already tracked
        result = await db.execute(
            select(EmailEvent).where(
                EmailEvent.email_log_id == email_log.id,
                EmailEvent.event_type == EventType.OPEN
            )
        )
        existing_event = result.scalar_one_or_none()
        
        if not existing_event:
            # Create open event
            event = EmailEvent(
                email_log_id=email_log.id,
                event_type=EventType.OPEN,
                user_agent=request.headers.get("user-agent"),
                ip_address=request.client.host
            )
            db.add(event)
            await db.commit()
    
    # Return 1x1 transparent pixel
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    
    return Response(content=pixel, media_type="image/gif")


@router.get("/click/{tracking_id}")
async def track_click(
    tracking_id: str,
    url: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Track email click event and redirect."""
    # Find email log
    result = await db.execute(
        select(EmailLog).where(EmailLog.tracking_id == tracking_id)
    )
    email_log = result.scalar_one_or_none()
    
    if email_log:
        # Create click event
        event = EmailEvent(
            email_log_id=email_log.id,
            event_type=EventType.CLICK,
            clicked_url=url,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host
        )
        db.add(event)
        await db.commit()
    
    # Redirect to original URL
    return RedirectResponse(url=url)


@router.get("/unsubscribe")
async def unsubscribe(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle unsubscribe request."""
    # Find email log
    result = await db.execute(
        select(EmailLog).where(EmailLog.tracking_id == id)
    )
    email_log = result.scalar_one_or_none()
    
    if email_log:
        # Create unsubscribe event
        event = EmailEvent(
            email_log_id=email_log.id,
            event_type=EventType.UNSUBSCRIBE
        )
        db.add(event)
        await db.commit()
    
    return {"message": "You have been unsubscribed successfully"}
