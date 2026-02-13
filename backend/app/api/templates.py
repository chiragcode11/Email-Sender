from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from app.database import get_db
from app.models.user import User
from app.models.template import EmailTemplate
from app.schemas.template import EmailTemplateCreate, EmailTemplateResponse, EmailTemplateUpdate
from app.api.auth import get_current_user

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: EmailTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new email template."""
    new_template = EmailTemplate(
        user_id=current_user.id,
        **template_data.model_dump()
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    return new_template


@router.get("", response_model=List[EmailTemplateResponse])
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all templates for the current user."""
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.user_id == current_user.id)
    )
    templates = result.scalars().all()
    return templates


@router.get("/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template."""
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == template_id,
            EmailTemplate.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.patch("/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a template."""
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == template_id,
            EmailTemplate.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Update fields
    for field, value in template_data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a template."""
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == template_id,
            EmailTemplate.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    await db.delete(template)
    await db.commit()
