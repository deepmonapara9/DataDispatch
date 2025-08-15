# AI-Powered Newsletter Platform

A complete newsletter platform with AI content generation, subscription management, and automated email delivery.

## Features

- 🌐 Modern responsive frontend with subscription/unsubscribe forms
- 🚀 FastAPI backend with SQLite database
- 🤖 AI-powered content generation using Ollama or OpenAI
- 📧 Gmail SMTP integration for email delivery
- ⏰ Automated weekly newsletter generation and sending
- 📱 Mobile-friendly and SEO-optimized
- 🔒 Privacy-focused with unsubscribe functionality

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

### 5. Frontend Deployment

Deploy the `frontend/` folder to:
- GitHub Pages
- Netlify
- Vercel
- Any static hosting service

Update the `API_BASE_URL` in `frontend/script.js` to point to your deployed backend.

### 6. AI Setup

**Option A: Ollama (Local)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
```

**Option B: OpenAI API**
Add your OpenAI API key to the `.env` file.

### 7. Setup Weekly Cron Job

```bash
# Edit crontab
crontab -e

# Add this line to run every Monday at 9 AM
0 9 * * 1 cd /path/to/Newsletter && python scripts/weekly_newsletter.py
```

## Deployment

### Backend (Render/Railway)

1. **Render:**
   - Connect your GitHub repository
   - Set build command: `pip install -r backend/requirements.txt`
   - Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

2. **Railway:**
   - Connect GitHub repository
   - Railway will auto-detect Python and FastAPI
   - Add environment variables
   - Deploy

### Frontend (Netlify/GitHub Pages)

1. **Netlify:**
   - Drag and drop the `frontend/` folder
   - Or connect GitHub repository with build settings:
     - Publish directory: `frontend`

2. **GitHub Pages:**
   - Push to GitHub
   - Enable GitHub Pages in repository settings
   - Set source to `frontend/` folder

## API Endpoints

- `POST /subscribe` - Subscribe to newsletter
- `POST /unsubscribe` - Unsubscribe from newsletter
- `GET /health` - Health check

## Usage

1. Users visit your frontend website
2. They enter their email to subscribe
3. Weekly cron job generates AI content and sends newsletters
4. Users can unsubscribe anytime via the link in emails

## Security Notes

- Use Gmail App Passwords, not regular passwords
- Keep your `.env` file secure and never commit it
- The platform respects privacy and includes unsubscribe functionality
- CORS is configured for your specific frontend domain

## Support

For issues or questions, please check the documentation or create an issue in the repository.
