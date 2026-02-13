#!/bin/bash

# Email Automation System - Frontend Setup Script

echo "🎨 Setting up Email Automation Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure the backend is running on http://localhost:8000"
echo "2. Start the frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Frontend will be available at: http://localhost:3000"
