from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.api.auth import get_current_user
from app.models.user import User
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])


class GenerateEmailRequest(BaseModel):
    context: str
    recipient_data: Dict[str, Any]
    tone: str = "professional"
    length: str = "medium"
    custom_body: Optional[str] = None


class GenerateEmailResponse(BaseModel):
    subject: str
    html_content: str
    plain_text: str


@router.post("/generate", response_model=GenerateEmailResponse)
async def generate_email(
    request: GenerateEmailRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate email content using AI."""
    try:
        result = await ai_service.generate_email_content(
            context=request.context,
            recipient_data=request.recipient_data,
            tone=request.tone,
            length=request.length,
            custom_body=request.custom_body
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}"
        )
