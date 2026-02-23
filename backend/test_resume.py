import asyncio
import os
import sys

sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import get_current_user
from app.models.user import User
from app.database import AsyncSessionLocal
from sqlalchemy import text

# Override authentication
async def override_get_current_user():
    return User(id=1, username="testuser", email="test@example.com")

app.dependency_overrides[get_current_user] = override_get_current_user

# Create Test Client
client = TestClient(app)

async def test_resume():
    # Make sure campaign 1 is paused
    async with AsyncSessionLocal() as db:
        await db.execute(text("UPDATE campaigns SET status = 'paused' WHERE id = 1"))
        await db.commit()
    
    print("Testing /campaigns/1/retry endpoint...")
    response = client.post("/campaigns/1/retry")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    if os.path.basename(os.getcwd()) != 'backend':
        os.chdir('backend')
    asyncio.run(test_resume())
