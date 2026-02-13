#!/bin/bash

# Email Automation System - Setup Script

echo "🚀 Setting up Email Automation System..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your configuration (Gmail, Gemini API key, etc.)"
fi

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! redis-cli ping &> /dev/null; then
    echo "⚠️  Redis is not running. Please start Redis:"
    echo "   brew install redis"
    echo "   brew services start redis"
else
    echo "✅ Redis is running"
fi

# Initialize database
echo "🗄️  Initializing database..."
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
print('✅ Database initialized')
"

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env with your configuration"
echo "2. Start the backend server: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start Celery worker: cd backend && source venv/bin/activate && celery -A app.celery_app worker --loglevel=info"
echo "4. Start Celery beat: cd backend && source venv/bin/activate && celery -A app.celery_app beat --loglevel=info"
echo ""
echo "🌐 API will be available at: http://localhost:8000"
echo "📚 API docs will be at: http://localhost:8000/docs"
