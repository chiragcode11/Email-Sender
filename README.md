# Email Automation System

A full-stack email automation platform for sending personalized bulk emails with AI-generated content, tracking, spam prevention, and warm-up functionality.

## Features

✅ **Multi-source Data Import** - CSV, Excel, MongoDB, Google Sheets  
✅ **AI-Powered Content Generation** - Gemini 3 Flash for personalized emails  
✅ **WYSIWYG Email Editor** - Rich text editing with personalization  
✅ **Complete Tracking** - Opens, clicks, bounces, delivery status  
✅ **Automatic Warm-up** - Gradual sending increase to build reputation  
✅ **Spam Filter Testing** - Pre-send spam score checking  
✅ **Scheduling** - One-time scheduled campaigns  
✅ **A/B Testing** - Test different subjects and content  
✅ **Real-time Dashboard** - WebSocket updates for live progress  
✅ **Rate Limiting** - Respect Gmail's 500 emails/day limit  

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLite** - Local database
- **Celery + Redis** - Background task processing
- **Gemini 3 Flash** - AI content generation
- **Gmail SMTP** - Email sending

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast development
- **TailwindCSS** - Styling
- **Socket.IO** - Real-time updates

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis
- Gmail account with App Password

### Backend Setup

```bash
# Run setup script
chmod +x setup-backend.sh
./setup-backend.sh

# Edit configuration
nano backend/.env

# Start backend server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# In separate terminals, start Celery
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
```

### Frontend Setup

```bash
# Run setup script
chmod +x setup-frontend.sh
./setup-frontend.sh

# Start frontend
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

## Configuration

Edit `backend/.env` with your settings:

```env
# Gmail SMTP
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Secret Key (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key
```

### Getting Gmail App Password

1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate new
4. Copy the 16-character password

### Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy the key

## API Documentation

Once the backend is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Project Structure

```
email-automation/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── parsers/      # Data import parsers
│   │   ├── tasks/        # Celery tasks
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/             # React frontend (coming soon)
└── README.md
```

## Usage

### 1. Create Account
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"password123"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=user&password=password123"
```

### 3. Create Campaign
Use the API docs at http://localhost:8000/docs for interactive testing.

## Spam Prevention

The system includes multiple spam prevention measures:
- Spam trigger word detection
- Subject line analysis
- HTML/text ratio checking
- Proper email headers (List-Unsubscribe, etc.)
- Gradual warm-up to build sender reputation
- SpamAssassin integration (optional)

## Warm-up Strategy

The warm-up engine automatically increases sending volume:
- Day 1: 20 emails
- Day 2: 40 emails
- Day 3: 80 emails
- ...continues until reaching Gmail's limit

## Tracking

All emails include:
- **Open tracking**: Invisible 1x1 pixel
- **Click tracking**: URL redirect service
- **Bounce handling**: IMAP monitoring (optional)

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Style
```bash
black app/
flake8 app/
```

## Roadmap

- [x] Backend API
- [x] Database models
- [x] Email sending
- [x] AI integration
- [x] Tracking
- [x] Spam checking
- [x] Frontend UI
- [x] WYSIWYG editor
- [x] Dashboard
- [x] Analytics
- [x] WebSocket integration
- [ ] Recipient import UI
- [ ] A/B testing UI
- [ ] Email templates library
- [ ] Advanced analytics
- [ ] Deployment guide

## License

MIT

## Support

For issues and questions, please open a GitHub issue.
