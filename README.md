# 📧 DataDispatch - AI-Powered Newsletter Platform

A complete full-stack AI-powered newsletter platform built with FastAPI, React, SQLite, and Ollama/OpenAI integration.

## ✨ Features

- 🤖 **AI Content Generation** - Automatic newsletter creation using Ollama (local) or OpenAI
- 📧 **Email Management** - Gmail SMTP integration with batch sending
- 🌐 **Modern Web Interface** - React frontend for subscriptions/unsubscriptions
- 📊 **Subscriber Management** - SQLite database with full CRUD operations
- 🔒 **Privacy Focused** - Local AI processing with Ollama support
- 📱 **Responsive Design** - Mobile-friendly subscription interface

## 🏗️ Architecture

```
DataDispatch/
├── backend/           # FastAPI REST API
│   ├── main.py       # API endpoints
│   ├── database.py   # Database models & operations
│   ├── models.py     # Pydantic models
│   └── newsletter.db # SQLite database
├── react-frontend/    # React SPA
│   ├── src/          # React components
│   └── public/       # Static assets
├── ai_agent/         # Content generation
│   ├── content_generator.py
│   └── prompts.py
├── mailer/           # Email sending
│   └── email_sender.py
├── logs/             # Application logs
└── send_to_all.py    # Newsletter sending script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Ollama (for local AI) or OpenAI API key
- Gmail account with App Password

### 1. Clone & Setup

```bash
git clone <repository-url>
cd Newsletter
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Email Configuration
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AI Configuration
AI_PROVIDER=ollama                    # or 'openai'
OLLAMA_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=your-openai-key       # if using OpenAI

# Newsletter Settings
NEWSLETTER_FROM_NAME=Your Newsletter
DATABASE_URL=sqlite:///./backend/newsletter.db
```

### 3. Start Services

**Backend API:**
```bash
source .venv/bin/activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**React Frontend:**
```bash
cd react-frontend
npm install
npm start  # Development server on port 3001
# or
npm run build && npx serve -s build -p 3002  # Production build
```

**Ollama (if using local AI):**
```bash
ollama serve
ollama pull llama3.2:1b  # Pull required model
```

## 🔧 Usage

### Web Interface
- **Frontend**: http://localhost:3001 (dev) or http://localhost:3002 (production)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Send Newsletter
```bash
# With AI-generated content
python send_to_all.py --subject "Weekly Update" --generate-content

# With custom HTML file
python send_to_all.py --subject "Custom Newsletter" --file sample_newsletter.html
```

### API Endpoints

- `POST /subscribe` - Subscribe email
- `POST /unsubscribe` - Unsubscribe email
- `GET /health` - Health check
- `GET /stats` - Subscriber statistics

## 🤖 AI Integration

### Ollama (Local LLM)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3.2:1b
ollama pull mistral:latest

# Start service
ollama serve
```

### OpenAI
Set `AI_PROVIDER=openai` and add your API key to `.env`.

## 📧 Email Setup

### Gmail Configuration
1. Enable 2-Factor Authentication
2. Generate App Password: Google Account → Security → App passwords
3. Use the 16-character app password in `.env`

## 📊 Database Management

The platform uses SQLite with automatic initialization. Database file: `backend/newsletter.db`

### Direct Database Access
```bash
cd backend
sqlite3 newsletter.db
.tables
SELECT * FROM subscribers;
```

## 🧪 Testing

### Test Email Configuration
```bash
cd mailer
python email_sender.py
```

### Test API
```bash
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/subscribe -H "Content-Type: application/json" -d '{"email":"test@example.com"}'
```

## 🚀 Production Deployment

### Build Frontend
```bash
cd react-frontend
npm run build
```

### Run Backend
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Serve Frontend
```bash
npx serve -s react-frontend/build -p 3000
```

## 📝 Current Status

✅ **Working Components:**
- FastAPI backend with full CRUD operations
- React frontend with subscription management
- AI content generation (Ollama + OpenAI support)
- Email sending with Gmail SMTP
- SQLite database with 13+ active subscribers
- Automated newsletter sending

✅ **Successfully Tested:**
- Newsletter sending to all subscribers (100% success rate)
- AI content generation with llama3.2:1b model
- Frontend/backend integration
- Email delivery and unsubscribe links

## 🔧 Troubleshooting

### Common Issues

**White screen in React:**
- Use production build: `npm run build && npx serve -s build`
- Check browser console for errors
- Ensure backend CORS is configured for frontend URL

**Email sending fails:**
- Verify Gmail App Password (not regular password)
- Check SMTP credentials in `.env`
- Test connection: `python mailer/email_sender.py`

**AI generation fails:**
- Ensure Ollama is running: `ollama serve`
- Check model availability: `ollama list`
- Verify model name in `.env` matches available models

## 📄 License

MIT License - Feel free to use this project for your newsletter needs!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**DataDispatch** - Powering intelligent newsletters with AI 🚀
