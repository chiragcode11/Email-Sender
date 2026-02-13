from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Email Automation System"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./email_automation.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Gmail SMTP
    GMAIL_EMAIL: str
    GMAIL_APP_PASSWORD: str
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # Gemini AI
    GEMINI_API_KEY: str

    # Cerebras AI
    CEREBRAS_API_KEY: str = ""
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "email_automation"
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = "credentials.json"
    
    # Email Tracking
    TRACKING_DOMAIN: str = "http://localhost:8000"
    TRACKING_PIXEL_ROUTE: str = "/track/open"
    TRACKING_CLICK_ROUTE: str = "/track/click"
    
    # Rate Limiting
    DEFAULT_DAILY_LIMIT: int = 500
    DEFAULT_HOURLY_LIMIT: int = 50
    
    # Warm-up Settings
    WARMUP_ENABLED: bool = True
    WARMUP_START_VOLUME: int = 20
    WARMUP_GROWTH_RATE: float = 2.0
    WARMUP_MAX_DAYS: int = 14
    
    # SpamAssassin
    SPAMASSASSIN_HOST: str = "localhost"
    SPAMASSASSIN_PORT: int = 783
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # WebSocket
    WEBSOCKET_CORS_ALLOWED_ORIGINS: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
