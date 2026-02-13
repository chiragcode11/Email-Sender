from celery import shared_task
from typing import Dict, Any, List

from app.celery_app import celery_app
from app.services.ai_service import ai_service


@celery_app.task(name="app.tasks.ai_tasks.generate_email_content")
def generate_email_content(
    context: str,
    recipient_data: Dict[str, Any],
    tone: str = "professional",
    length: str = "medium",
    custom_body: str = None
) -> Dict[str, str]:
    """
    Generate email content using AI.
    This is a Celery task that runs asynchronously.
    """
    import asyncio
    return asyncio.run(
        ai_service.generate_email_content(context, recipient_data, tone, length, custom_body)
    )


@celery_app.task(name="app.tasks.ai_tasks.generate_bulk_emails")
def generate_bulk_emails(
    context: str,
    recipients: List[Dict[str, Any]],
    tone: str = "professional",
    length: str = "medium"
) -> List[Dict[str, str]]:
    """Generate emails for multiple recipients."""
    import asyncio
    return asyncio.run(
        ai_service.generate_bulk_emails(context, recipients, tone, length)
    )


@celery_app.task(name="app.tasks.ai_tasks.understand_data_schema")
def understand_data_schema(sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Understand data schema using AI."""
    import asyncio
    return asyncio.run(
        ai_service.understand_data_schema(sample_data)
    )


@celery_app.task(name="app.tasks.ai_tasks.generate_ab_variants")
def generate_ab_variants(
    original_subject: str,
    original_content: str,
    variant_type: str = "subject"
) -> Dict[str, str]:
    """Generate A/B test variants."""
    import asyncio
    return asyncio.run(
        ai_service.generate_ab_variants(original_subject, original_content, variant_type)
    )
