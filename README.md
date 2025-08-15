# DataDispatch - AI-Powered Newsletter Platform

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
├── auto_update_newsletter.py  # 🆕 Dynamic content updater
├── generate_newsletter.sh     # 🆕 Quick generation script
├── sample_newsletter.html     # 🆕 Live preview of generated content
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

### 7. 🆕 Quick Content Generation

**Generate fresh newsletter content instantly:**

```bash
# One-time generation
python auto_update_newsletter.py

# Generate and open in browser
python auto_update_newsletter.py --open

# Continuous updates every 5 minutes
python auto_update_newsletter.py --watch

# Quick script
./generate_newsletter.sh
```

**Your `sample_newsletter.html` file will automatically update with fresh AI-generated content!**

### 8. Setup Weekly Cron Job

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
- `GET /stats` - Get subscriber statistics

## 🚀 Dynamic Content Generation

### Quick Commands

| Command | Description |
|---------|-------------|
| `python auto_update_newsletter.py` | Generate fresh content once |
| `python auto_update_newsletter.py --open` | Generate + open in browser |
| `python auto_update_newsletter.py --watch` | Continuous updates (5min intervals) |
| `./generate_newsletter.sh` | Simple script wrapper |
| `python ai_agent/content_generator.py` | Test AI generation only |

### AI Models Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **mistral:latest** | 4.4GB | ~30s | ⭐⭐⭐⭐⭐ | **Production newsletters** |
| **llama3.2:1b** | 1.3GB | ~3s | ⭐⭐⭐ | Quick testing |
| **OpenAI GPT-3.5** | API | ~2s | ⭐⭐⭐⭐ | Cloud-based option |

### Features

- **🔄 Auto-updating**: `sample_newsletter.html` updates automatically
- **💾 Backup system**: Timestamped backups of all generated content
- **🌐 Browser integration**: Auto-opens updated newsletter
- **⏰ Watch mode**: Continuous generation for live updates
- **🎯 Template integration**: AI content wrapped in beautiful email template

## Usage

### For Newsletter Platform:
1. Users visit your frontend website
2. They enter their email to subscribe
3. Weekly cron job generates AI content and sends newsletters
4. Users can unsubscribe anytime via the link in emails

### For Content Development:
1. **Generate fresh content**: `python auto_update_newsletter.py --open`
2. **Preview in browser**: Content auto-opens in beautiful newsletter template
3. **Iterate quickly**: Run script again for new AI-generated content
4. **Copy for production**: Use generated content in actual newsletters

## 🎯 Quick Start Workflow

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 2. Install and start Ollama
ollama serve
ollama pull mistral:latest

# 3. Generate your first newsletter
python auto_update_newsletter.py --open

# 4. Start the backend (optional, for subscriptions)
cd backend && uvicorn main:app --reload
```

**That's it! Your AI newsletter system is ready! 🚀**

## Security Notes

- Use Gmail App Passwords, not regular passwords
- Keep your `.env` file secure and never commit it
- The platform respects privacy and includes unsubscribe functionality
- CORS is configured for your specific frontend domain
- Local AI models (Ollama) keep your content generation private
- Automatic backups ensure content is never lost

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
