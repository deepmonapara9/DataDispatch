# DataDispatch - AI-Powered Newsletter Platform

A complete newsletter platform with AI content generation, subscription management, and automated email delivery.

## Features

- 🌐 Modern responsive frontend with subscription/unsubscribe forms
- 🚀 FastAPI backend with SQLite database
- 🤖 AI-powered content generation using Ollama (Mistral/Llama) or OpenAI
- 📧 Gmail SMTP integration for email delivery
- ⏰ Automated weekly newsletter generation and sending
- 📱 Mobile-friendly and SEO-optimized
- 🔒 Privacy-focused with unsubscribe functionality- AI-Powered Newsletter Platform

A complete newsletter platform with AI content generation, subscription management, automated email delivery, and dynamic content updates.

## Features

- 🌐 Modern responsive frontend with subscription/unsubscribe forms
- 🚀 FastAPI backend with SQLite database
- 🤖 AI-powered content generation using Ollama (Mistral/Llama) or OpenAI
- 📧 Gmail SMTP integration for email delivery
- ⏰ Automated weekly newsletter generation and sending
- � **Dynamic content updates** - Auto-refresh newsletter with fresh AI content
- �📱 Mobile-friendly and SEO-optimized
- 🔒 Privacy-focused with unsubscribe functionality
- 💾 Automatic backup system for generated content

## Project Structure

```
Newsletter/
├── frontend/               # Static website files
│   ├── index.html         # Landing page
│   ├── unsubscribe.html   # Unsubscribe page
│   ├── style.css          # Styles
│   └── script.js          # JavaScript functionality
├── backend/               # FastAPI backend
│   ├── main.py           # FastAPI application
│   ├── database.py       # Database models and operations
│   ├── models.py         # Pydantic models
│   └── requirements.txt  # Python dependencies
├── ai_agent/             # AI content generation
│   ├── content_generator.py  # AI newsletter generator
│   └── prompts.py           # AI prompts and templates
├── mailer/               # Email functionality
│   └── email_sender.py   # SMTP email sending
├── scripts/              # Automation scripts
│   └── weekly_newsletter.py  # Cron job script
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Setup Instructions

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `SMTP_EMAIL`: Your Gmail address
- `SMTP_PASSWORD`: Gmail App Password
- `FRONTEND_URL`: Your frontend URL (for CORS)
- `OPENAI_API_KEY`: (Optional) For OpenAI instead of Ollama

### 3. Database Setup

The SQLite database will be created automatically when you first run the backend.

### 4. Start Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Frontend Setup

Open `frontend/index.html` in a web browser or serve it using a simple HTTP server:

```bash
# Python 3
cd frontend && python -m http.server 3000

# Node.js
cd frontend && npx serve .
```

Update the `API_BASE_URL` in `frontend/script.js` to point to your backend server.

### 6. AI Setup

**Recommended: Ollama (Local)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull recommended models
ollama pull mistral:latest    # Best quality (4.4GB)
ollama pull llama3.2:1b      # Faster, smaller (1.3GB)
```

**Alternative: OpenAI API**
Add your OpenAI API key to the `.env` file and set `AI_PROVIDER=openai`.

### 7. Setup Weekly Cron Job

```bash
# Edit crontab
crontab -e

# Add this line to run every Monday at 9 AM
0 9 * * 1 cd /path/to/Newsletter && python scripts/weekly_newsletter.py
```

## API Endpoints

- `POST /subscribe` - Subscribe to newsletter
- `POST /unsubscribe` - Unsubscribe from newsletter
- `GET /health` - Health check
- `GET /stats` - Get subscriber statistics

## Usage

1. Users visit your frontend website
2. They enter their email to subscribe
3. Weekly cron job generates AI content and sends newsletters
4. Users can unsubscribe anytime via the link in emails

## Quick Start

```bash
# 1. Setup (automated script)
./setup.sh

# 2. Edit environment file with your credentials
nano .env

# 3. Start the backend
./setup.sh dev
```

**That's it! Your AI newsletter system is ready! 🚀**

## Security Notes

- Use Gmail App Passwords, not regular passwords
- Keep your `.env` file secure and never commit it
- The platform respects privacy and includes unsubscribe functionality
- CORS is configured for your specific frontend domain
- Local AI models (Ollama) keep your content generation private

## Troubleshooting

### AI Generation Issues
```bash
# Check Ollama status
ollama list

# Test AI connection
python ai_agent/content_generator.py

# Check if model is available
ollama pull mistral:latest
```

### Backend Issues
```bash
# Test backend
curl http://localhost:8000/health

# Check database
python -c "from backend.database import init_db; init_db()"
```

### Environment Issues
```bash
# Verify environment variables
python -c "import os; print(os.getenv('OLLAMA_MODEL'))"
```

## Support

For issues or questions, please check the documentation or create an issue in the repository.
