from openai import AsyncOpenAI
import json
from typing import Dict, Any, List, Optional
from app.config import settings


class AIService:
    """Service for AI-powered content generation using Cerebras (Llama 3.3 70B)."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1"
        )
        self.model = "llama3.3-70b"
    
    async def generate_email_content(
        self,
        context: str,
        recipient_data: Dict[str, Any],
        tone: str = "professional",
        length: str = "medium",
        custom_body: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate personalized email content using Cerebras.
        
        Args:
            context: User's instructions for email content key points.
            recipient_data: Recipient personalization data.
            tone: Email tone (professional, casual, friendly, formal).
            length: Email length (short, medium, long).
            custom_body: Optional custom draft/body to refine or use as base.
        
        Returns:
            Dict with 'subject', 'html_content', and 'plain_text' keys.
        """
        prompt = self._build_email_generation_prompt(context, recipient_data, tone, length, custom_body)
        
        completion = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert email copywriter. You write professional, engaging, and personalized emails."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.7,
            top_p=1,
            max_tokens=1024,
            stream=False
        )
        
        content = completion.choices[0].message.content
        
        # Extract subject and body
        subject, html_content, plain_text = self._parse_email_response(content)
        
        return {
            "subject": subject,
            "html_content": html_content,
            "plain_text": plain_text
        }
    
    async def generate_bulk_emails(
        self,
        context: str,
        recipients: List[Dict[str, Any]],
        tone: str = "professional",
        length: str = "medium"
    ) -> List[Dict[str, str]]:
        """Generate personalized emails for multiple recipients."""
        emails = []
        
        for recipient in recipients:
            email = await self.generate_email_content(context, recipient, tone, length)
            emails.append({
                "recipient_email": recipient.get("email"),
                **email
            })
        
        return emails
    
    async def understand_data_schema(self, sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use AI to understand and suggest field mappings for imported data.
        """
        prompt = f"""
Analyze this sample data and suggest:
1. Which fields could be used for personalization
2. Suggested field mappings (email, first_name, last_name, etc.)
3. Any interesting patterns or insights

Sample Data:
{json.dumps(sample_data[:5], indent=2)}

Respond ONLY in JSON format with:
{{
    "suggested_mappings": {{"field_name": "purpose"}},
    "personalization_fields": ["field1", "field2"],
    "insights": "description"
}}
"""
        try:
            completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a data analyst helper. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            return json.loads(response_text)
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return {
                "suggested_mappings": {},
                "personalization_fields": [],
                "insights": "Could not parse data"
            }
    
    async def generate_ab_variants(
        self,
        original_subject: str,
        original_content: str,
        variant_type: str = "subject"
    ) -> Dict[str, str]:
        """
        Generate A/B test variants.
        """
        if variant_type == "subject":
            prompt = f"""
Create an alternative email subject line for A/B testing.

Original Subject: {original_subject}

Requirements:
- Different approach but same goal
- Similar length
- Compelling and engaging

Respond with just the alternative subject line, nothing else.
"""
            completion = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.8
            )
            return {
                "variant_subject": completion.choices[0].message.content.strip().replace("Subject: ", ""),
                "variant_content": original_content
            }
        
        elif variant_type == "content":
            prompt = f"""
Create an alternative email content for A/B testing.

Original Content:
{original_content}

Requirements:
- Different structure but same message
- Similar length
- Engaging and clear

Respond with the alternative content in HTML format.
"""
            completion = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.8
            )
            return {
                "variant_subject": original_subject,
                "variant_content": completion.choices[0].message.content.strip()
            }
        
        else:  # both
            # TODO: Improve concurrency here with asyncio.gather if needed frequently
            subject_variant = await self.generate_ab_variants(
                original_subject, original_content, "subject"
            )
            content_variant = await self.generate_ab_variants(
                original_subject, original_content, "content"
            )
            return {
                "variant_subject": subject_variant["variant_subject"],
                "variant_content": content_variant["variant_content"]
            }
    
    def _build_email_generation_prompt(
        self,
        context: str,
        recipient_data: Dict[str, Any],
        tone: str,
        length: str,
        custom_body: Optional[str] = None
    ) -> str:
        """Build prompt for email generation."""
        recipient_info = "\n".join([f"- {k}: {v}" for k, v in recipient_data.items()])
        
        length_guide = {
            "short": "2-3 paragraphs",
            "medium": "4-5 paragraphs",
            "long": "6-8 paragraphs"
        }
        
        body_instruction = ""
        if custom_body:
             body_instruction = f"""
THE USER PROVIDED THE FOLLOWING CUSTOM DRAFT/BODY. USE IT AS THE BASE AND REFINE IT.
IMPROVE ITS CLARITY AND TONE ACCORDING TO REQUIREMENTS, BUT KEEP THE CORE MESSAGE.

CUSTOM DRAFT:
{custom_body}
"""
        
        prompt = f"""
Generate a personalized email based on the following:

CONTEXT/INSTRUCTIONS:
{context}

{body_instruction}

RECIPIENT INFORMATION:
{recipient_info}

REQUIREMENTS:
- Tone: {tone}
- Length: {length_guide.get(length, "4-5 paragraphs")}
- Personalize using the recipient information provided.
- Include a clear call-to-action.
- Format in HTML for email.

RESPONSE FORMAT:
You MUST respond in this exact format, with no markdown code blocks (```):

SUBJECT: [email subject line]

HTML:
[HTML formatted email content]

PLAIN TEXT:
[Plain text version of the email]
"""
        return prompt
    
    def _parse_email_response(self, content: str) -> tuple:
        """Parse AI response into subject, HTML, and plain text."""
        lines = content.strip().split("\n")
        
        subject = ""
        html_content = ""
        plain_text = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.upper().startswith("SUBJECT:"):
                subject = line[8:].strip()
                current_section = "subject"
            elif line.upper().startswith("HTML:"):
                current_section = "html"
            elif line.upper().startswith("PLAIN TEXT:"):
                current_section = "plain"
            else:
                if current_section == "html":
                    html_content += line + "\n"
                elif current_section == "plain":
                    plain_text += line + "\n"
        
        # Clean up
        html_content = html_content.strip().replace("```html", "").replace("```", "")
        plain_text = plain_text.strip()
        
        # Fallback if parsing failed
        if not subject and not html_content:
             # Try to guess if raw content was returned
             subject = "Generated Email"
             html_content = f"<p>{content.replace(chr(10), '<br>')}</p>"
             plain_text = content

        if not subject:
            subject = "Your Personalized Email"
        if not html_content:
             html_content = f"<p>{plain_text or content}</p>"
        
        return subject, html_content, plain_text


# Singleton instance
ai_service = AIService()
