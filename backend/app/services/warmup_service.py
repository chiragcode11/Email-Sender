from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warmup_settings import WarmupSettings
from app.models.user import User


class WarmupService:
    """Service for managing email sending warm-up."""
    
    async def get_or_create_warmup_settings(
        self,
        user_id: int,
        db: AsyncSession
    ) -> WarmupSettings:
        """Get or create warmup settings for a user."""
        result = await db.execute(
            select(WarmupSettings).where(WarmupSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            from app.config import settings as app_settings
            settings = WarmupSettings(
                user_id=user_id,
                is_enabled=app_settings.WARMUP_ENABLED,
                start_volume=app_settings.WARMUP_START_VOLUME,
                growth_rate=app_settings.WARMUP_GROWTH_RATE,
                max_days=app_settings.WARMUP_MAX_DAYS,
                current_daily_limit=app_settings.WARMUP_START_VOLUME
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        
        return settings
    
    async def check_can_send(
        self,
        user_id: int,
        db: AsyncSession,
        count: int = 1
    ) -> Dict[str, Any]:
        """
        Check if user can send emails based on warm-up limits.
        
        Returns:
            Dict with 'can_send', 'remaining', 'limit', 'reset_at'
        """
        settings = await self.get_or_create_warmup_settings(user_id, db)
        
        if not settings.is_enabled:
            return {
                "can_send": True,
                "remaining": 999999,
                "limit": 999999,
                "reset_at": None
            }
        
        # Check if we need to reset daily counter
        now = datetime.utcnow()
        if settings.last_reset_at:
            hours_since_reset = (now - settings.last_reset_at).total_seconds() / 3600
            if hours_since_reset >= 24:
                await self._reset_daily_counter(settings, db)
        
        remaining = settings.current_daily_limit - settings.emails_sent_today
        can_send = remaining >= count
        
        # Calculate next reset time
        reset_at = settings.last_reset_at + timedelta(days=1) if settings.last_reset_at else now + timedelta(days=1)
        
        return {
            "can_send": can_send,
            "remaining": max(0, remaining),
            "limit": settings.current_daily_limit,
            "reset_at": reset_at
        }
    
    async def record_sent_emails(
        self,
        user_id: int,
        count: int,
        db: AsyncSession
    ):
        """Record that emails were sent."""
        settings = await self.get_or_create_warmup_settings(user_id, db)
        settings.emails_sent_today += count
        await db.commit()
    
    async def update_warmup_progress(
        self,
        user_id: int,
        db: AsyncSession
    ):
        """Update warmup progress (increase daily limit)."""
        settings = await self.get_or_create_warmup_settings(user_id, db)
        
        if not settings.is_enabled:
            return
        
        # Check if warmup is complete
        if settings.current_day >= settings.max_days:
            settings.is_enabled = False
            await db.commit()
            return
        
        # Increase daily limit
        new_limit = int(settings.start_volume * (settings.growth_rate ** settings.current_day))
        
        # Cap at Gmail's limit
        from app.config import settings as app_settings
        new_limit = min(new_limit, app_settings.DEFAULT_DAILY_LIMIT)
        
        settings.current_day += 1
        settings.current_daily_limit = new_limit
        settings.emails_sent_today = 0
        settings.last_reset_at = datetime.utcnow()
        
        await db.commit()
    
    async def _reset_daily_counter(
        self,
        settings: WarmupSettings,
        db: AsyncSession
    ):
        """Reset daily email counter."""
        settings.emails_sent_today = 0
        settings.last_reset_at = datetime.utcnow()
        await db.commit()
    
    async def update_performance_metrics(
        self,
        user_id: int,
        bounce_rate: float,
        spam_rate: float,
        db: AsyncSession
    ):
        """Update performance metrics and adjust warm-up if needed."""
        settings = await self.get_or_create_warmup_settings(user_id, db)
        
        settings.bounce_rate = bounce_rate
        settings.spam_rate = spam_rate
        
        # If bounce/spam rates are high, slow down warm-up
        if bounce_rate > 5.0 or spam_rate > 1.0:
            # Reduce daily limit by 20%
            settings.current_daily_limit = int(settings.current_daily_limit * 0.8)
            settings.growth_rate = max(1.5, settings.growth_rate - 0.2)
        
        await db.commit()


# Singleton instance
warmup_service = WarmupService()
