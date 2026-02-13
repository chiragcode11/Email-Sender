import re
from typing import Dict, List, Tuple
import socket


class SpamChecker:
    """Service for checking emails against spam filters."""
    
    # Common spam trigger words
    SPAM_WORDS = [
        "free", "winner", "cash", "prize", "urgent", "act now", "limited time",
        "click here", "buy now", "order now", "guarantee", "no obligation",
        "risk-free", "100%", "!!!!", "$$", "make money", "earn money",
        "work from home", "be your own boss", "multi-level marketing", "mlm"
    ]
    
    def check_email(self, subject: str, html_content: str, plain_text: str = "") -> Dict:
        """
        Check email for spam indicators.
        
        Returns:
            Dict with 'score', 'issues', and 'recommendations'
        """
        issues = []
        score = 0  # Lower is better
        
        # Check subject line
        subject_issues, subject_score = self._check_subject(subject)
        issues.extend(subject_issues)
        score += subject_score
        
        # Check content
        content_issues, content_score = self._check_content(html_content, plain_text)
        issues.extend(content_issues)
        score += content_score
        
        # Check HTML structure
        html_issues, html_score = self._check_html(html_content)
        issues.extend(html_issues)
        score += html_score
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues)
        
        # Determine spam likelihood
        if score < 3:
            likelihood = "Low"
        elif score < 7:
            likelihood = "Medium"
        else:
            likelihood = "High"
        
        return {
            "score": score,
            "likelihood": likelihood,
            "issues": issues,
            "recommendations": recommendations,
            "passed": score < 5
        }
    
    def _check_subject(self, subject: str) -> Tuple[List[str], int]:
        """Check subject line for spam indicators."""
        issues = []
        score = 0
        
        # Check length
        if len(subject) > 60:
            issues.append("Subject line is too long (>60 characters)")
            score += 1
        
        # Check for all caps
        if subject.isupper() and len(subject) > 5:
            issues.append("Subject line is in ALL CAPS")
            score += 2
        
        # Check for excessive punctuation
        if subject.count("!") > 1:
            issues.append("Too many exclamation marks in subject")
            score += 2
        
        # Check for spam words
        subject_lower = subject.lower()
        spam_words_found = [word for word in self.SPAM_WORDS if word in subject_lower]
        if spam_words_found:
            issues.append(f"Spam trigger words in subject: {', '.join(spam_words_found)}")
            score += len(spam_words_found)
        
        return issues, score
    
    def _check_content(self, html_content: str, plain_text: str) -> Tuple[List[str], int]:
        """Check email content for spam indicators."""
        issues = []
        score = 0
        
        # Use plain text if available, otherwise strip HTML
        content = plain_text if plain_text else re.sub(r'<[^>]+>', '', html_content)
        content_lower = content.lower()
        
        # Check for spam words
        spam_words_found = [word for word in self.SPAM_WORDS if word in content_lower]
        if len(spam_words_found) > 3:
            issues.append(f"Multiple spam trigger words found: {len(spam_words_found)}")
            score += 2
        
        # Check for excessive links
        link_count = html_content.count('href=')
        word_count = len(content.split())
        if word_count > 0 and link_count / word_count > 0.1:
            issues.append("Too many links relative to content")
            score += 2
        
        # Check for missing plain text
        if not plain_text:
            issues.append("No plain text version provided")
            score += 1
        
        return issues, score
    
    def _check_html(self, html_content: str) -> Tuple[List[str], int]:
        """Check HTML structure."""
        issues = []
        score = 0
        
        # Check HTML/text ratio
        text_content = re.sub(r'<[^>]+>', '', html_content)
        if len(html_content) > 0:
            ratio = len(text_content) / len(html_content)
            if ratio < 0.2:
                issues.append("HTML to text ratio is too low (too much HTML)")
                score += 2
        
        # Check for proper HTML structure
        if '<html' not in html_content.lower():
            issues.append("Missing proper HTML structure")
            score += 1
        
        # Check for image-only emails
        if html_content.count('<img') > 0 and len(text_content.strip()) < 50:
            issues.append("Email appears to be image-only")
            score += 3
        
        return issues, score
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        if any("ALL CAPS" in issue for issue in issues):
            recommendations.append("Use normal capitalization in subject line")
        
        if any("exclamation" in issue for issue in issues):
            recommendations.append("Reduce exclamation marks to 1 or none")
        
        if any("spam trigger words" in issue.lower() for issue in issues):
            recommendations.append("Replace spam trigger words with more natural language")
        
        if any("too many links" in issue for issue in issues):
            recommendations.append("Reduce number of links or add more content")
        
        if any("plain text" in issue for issue in issues):
            recommendations.append("Add a plain text version of your email")
        
        if any("HTML to text ratio" in issue for issue in issues):
            recommendations.append("Simplify HTML or add more text content")
        
        return recommendations
    
    async def check_with_spamassassin(self, email_content: str) -> Dict:
        """
        Check email with SpamAssassin (if available).
        
        Note: Requires SpamAssassin to be installed and running.
        """
        try:
            from app.config import settings
            
            # Connect to SpamAssassin
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((settings.SPAMASSASSIN_HOST, settings.SPAMASSASSIN_PORT))
            
            # Send email for checking
            request = f"CHECK SPAMC/1.0\r\nContent-length: {len(email_content)}\r\n\r\n{email_content}"
            sock.sendall(request.encode())
            
            # Get response
            response = sock.recv(4096).decode()
            sock.close()
            
            # Parse response
            lines = response.split('\r\n')
            score_line = [l for l in lines if 'Spam:' in l]
            
            if score_line:
                parts = score_line[0].split()
                is_spam = parts[1] == 'True'
                score = float(parts[2].split('/')[0])
                threshold = float(parts[2].split('/')[1])
                
                return {
                    "is_spam": is_spam,
                    "score": score,
                    "threshold": threshold,
                    "passed": not is_spam
                }
        
        except Exception as e:
            return {
                "error": str(e),
                "passed": True  # Assume passed if SpamAssassin not available
            }
        
        return {"passed": True}


# Singleton instance
spam_checker = SpamChecker()
