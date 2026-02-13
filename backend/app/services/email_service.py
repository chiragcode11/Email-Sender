import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, Any, Optional, List
import uuid
import re
from urllib.parse import quote

from app.config import settings


import ssl
import certifi

class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.from_email = settings.GMAIL_EMAIL
        self.password = settings.GMAIL_APP_PASSWORD
        
        if settings.DEBUG:
            # In DEBUG mode, attempt to create an unverified context directly
            # This helps avoid "unable to get local issuer certificate" on systems without proper certs
            try:
                # Try using certifi for CA certs even in debug mode, just to have a base
                self.ssl_context = ssl.create_default_context(cafile=certifi.where())
                self.ssl_context.check_hostname = False
                self.ssl_context.verify_mode = ssl.CERT_NONE
            except Exception:
                 # Fallback to completely unverified context
                try:
                    self.ssl_context = ssl._create_unverified_context()
                except AttributeError:
                    self.ssl_context = ssl.create_default_context()
                    self.ssl_context.check_hostname = False
                    self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            # Create standard SSL context using certifi
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_text: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        tracking_id: Optional[str] = None,
        track_opens: bool = True,
        track_clicks: bool = True
    ) -> Dict[str, Any]:
        """
        Send an email via SMTP.
        
        Returns:
            Dict with 'success', 'message_id', and optional 'error'
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{self.from_email}>" if from_name else self.from_email
            msg["To"] = to_email
            
            if reply_to:
                msg["Reply-To"] = reply_to
            
            # Add List-Unsubscribe header
            unsubscribe_url = f"{settings.TRACKING_DOMAIN}/unsubscribe?id={tracking_id}"
            msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
            msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
            
            # Add tracking
            if tracking_id:
                if track_opens:
                    html_content = self._add_tracking_pixel(html_content, tracking_id)
                
                if track_clicks:
                    html_content = self._add_click_tracking(html_content, tracking_id)
            
            # Add plain text part
            if plain_text:
                part1 = MIMEText(plain_text, "plain")
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)
            
            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host, 
                port=self.smtp_port,
                tls_context=self.ssl_context,
                start_tls=True
            ) as smtp:
                # TLS started automatically
                await smtp.login(self.from_email, self.password)
                response = await smtp.send_message(msg)
            
            return {
                "success": True,
                "message_id": msg["Message-ID"],
                "response": str(response)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_bulk_emails(
        self,
        emails: List[Dict[str, Any]],
        rate_limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Send multiple emails with optional rate limiting.
        
        Args:
            emails: List of email dicts with to_email, subject, html_content, etc.
            rate_limit: Max emails per hour (None for no limit)
        
        Returns:
            List of results for each email
        """
        results = []
        
        for email_data in emails:
            result = await self.send_email(**email_data)
            results.append({
                "to_email": email_data["to_email"],
                **result
            })
            
            # Rate limiting (simple delay)
            if rate_limit:
                import asyncio
                delay = 3600 / rate_limit  # seconds between emails
                await asyncio.sleep(delay)
        
        return results
    
    def _add_tracking_pixel(self, html_content: str, tracking_id: str) -> str:
        """Add invisible tracking pixel to HTML content."""
        pixel_url = f"{settings.TRACKING_DOMAIN}{settings.TRACKING_PIXEL_ROUTE}/{tracking_id}"
        tracking_pixel = f'<img src="{pixel_url}" width="1" height="1" style="display:none;" />'
        
        # Try to add before closing body tag
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"{tracking_pixel}</body>")
        else:
            html_content += tracking_pixel
        
        return html_content
    
    def _add_click_tracking(self, html_content: str, tracking_id: str) -> str:
        """Replace all links with tracking redirects."""
        # Find all href attributes
        def replace_link(match):
            original_url = match.group(1)
            
            # Skip mailto and anchor links
            if original_url.startswith(("mailto:", "#", "tel:")):
                return match.group(0)
            
            # Create tracking URL
            encoded_url = quote(original_url, safe="")
            tracking_url = f"{settings.TRACKING_DOMAIN}{settings.TRACKING_CLICK_ROUTE}/{tracking_id}?url={encoded_url}"
            
            return f'href="{tracking_url}"'
        
        # Replace all href attributes
        html_content = re.sub(r'href="([^"]+)"', replace_link, html_content)
        html_content = re.sub(r"href='([^']+)'", replace_link, html_content)
        
        return html_content
    
    def personalize_content(self, content: str, data: Dict[str, Any]) -> str:
        """
        Replace personalization variables in content.
        
        Variables format: {{variable_name}}
        """
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    async def test_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host, 
                port=self.smtp_port,
                tls_context=self.ssl_context,
                start_tls=True
            ) as smtp:
                # TLS started automatically
                await smtp.login(self.from_email, self.password)
            return True
        except Exception:
            return False


# Singleton instance
email_service = EmailService()
