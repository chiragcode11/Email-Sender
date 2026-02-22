from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api import auth, campaigns, tracking, templates, ai
from app.websocket import connection as ws_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    await init_db()
    
    # Auto-pause any campaigns stuck in SENDING state due to a crash/restart
    from app.database import AsyncSessionLocal
    from app.models.campaign import Campaign, CampaignStatus
    from sqlalchemy import select, update
    
    try:
        async with AsyncSessionLocal() as db:
            print("INFO: Checking for stuck campaigns...")
            result = await db.execute(
                select(Campaign).where(Campaign.status == CampaignStatus.SENDING)
            )
            stuck_campaigns = result.scalars().all()
            
            if stuck_campaigns:
                print(f"INFO: Found {len(stuck_campaigns)} campaigns stuck in SENDING state. Pausing them...")
                for campaign in stuck_campaigns:
                    campaign.status = CampaignStatus.PAUSED
                await db.commit()
                print("INFO: Stuck campaigns successfully paused.")
    except Exception as e:
        print(f"ERROR: Failed to handle stuck campaigns during startup: {e}")
        
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(campaigns.router)
app.include_router(tracking.router)
app.include_router(templates.router)
app.include_router(ai.router)
app.include_router(ws_connection.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Email Automation System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
