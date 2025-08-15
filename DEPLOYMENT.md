# Deployment Guide

This guide covers deploying your AI Newsletter Platform to production.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│  (Static Host)  │───▶│   (FastAPI)     │───▶│   (SQLite)      │
│                 │    │                 │    │                 │
│ • Netlify       │    │ • Render        │    │ • File-based    │
│ • GitHub Pages  │    │ • Railway       │    │ • Persistent    │
│ • Vercel        │    │ • Heroku        │    │   storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Email Service │
                    │  (Gmail SMTP)   │
                    │                 │
                    │ • App Passwords │
                    │ • Rate Limiting │
                    │ • Batch Sending │
                    └─────────────────┘
```

## Prerequisites

- Gmail account with App Passwords enabled
- GitHub account for code hosting
- Domain name (optional but recommended)

## Step 1: Backend Deployment

### Option A: Render (Recommended)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy Backend**
   - Connect your GitHub repository
   - Create a new Web Service
   - Settings:
     ```
     Build Command: pip install -r backend/requirements.txt
     Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Environment Variables**
   ```
   SMTP_EMAIL=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FRONTEND_URL=https://your-frontend-domain.com
   OPENAI_API_KEY=your-openai-key (optional)
   ```

4. **Database Storage**
   - Render provides persistent disk storage
   - SQLite file will be stored automatically

### Option B: Railway

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python/FastAPI

3. **Configure Settings**
   - Set root directory to `backend/`
   - Add environment variables (same as above)

### Option C: Heroku

1. **Create Heroku Account**
   - Install Heroku CLI
   - Login: `heroku login`

2. **Prepare for Deployment**
   ```bash
   # Create Procfile in backend/
   echo "web: uvicorn main:app --host=0.0.0.0 --port=$PORT" > backend/Procfile
   
   # Create runtime.txt
   echo "python-3.11.0" > backend/runtime.txt
   ```

3. **Deploy**
   ```bash
   cd backend
   heroku create your-newsletter-api
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

## Step 2: Frontend Deployment

### Option A: Netlify (Recommended)

1. **Prepare Frontend**
   - Update `API_BASE_URL` in `frontend/script.js`
   - Set it to your deployed backend URL

2. **Deploy to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop the `frontend/` folder
   - Or connect GitHub repository

3. **Custom Domain** (Optional)
   - Add your domain in Netlify settings
   - Update DNS records as instructed

### Option B: GitHub Pages

1. **Update Configuration**
   ```javascript
   // In frontend/script.js
   const API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```

2. **Enable GitHub Pages**
   - Go to repository Settings
   - Enable Pages from `main` branch, `frontend/` folder

### Option C: Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel --prod
   ```

## Step 3: Email Configuration

### Gmail App Password Setup

1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Enable 2FA if not already enabled

2. **Generate App Password**
   - Go to Google Account > Security
   - Select "App passwords"
   - Generate password for "Mail"
   - Use this password in your environment variables

3. **Test Email**
   ```bash
   cd backend
   python -c "
   from mailer.email_sender import EmailSender
   sender = EmailSender()
   sender.send_test_email()
   "
   ```

## Step 4: Domain and SSL

### Custom Domain Setup

1. **DNS Configuration**
   ```
   # For Netlify
   A record: @ -> 75.2.60.5
   CNAME record: www -> your-site.netlify.app
   
   # Backend subdomain
   CNAME record: api -> your-backend.onrender.com
   ```

2. **Update URLs**
   - Frontend: Update `API_BASE_URL` to `https://api.yourdomain.com`
   - Backend: Update `FRONTEND_URL` to `https://yourdomain.com`

## Step 5: Automation Setup

### Cron Job (For VPS/Dedicated Server)

If you have a VPS or dedicated server:

```bash
# Edit crontab
crontab -e

# Add weekly newsletter (Every Monday at 9 AM)
0 9 * * 1 cd /path/to/Newsletter && python scripts/weekly_newsletter.py

# Add monthly statistics (First day of month)
0 10 1 * * cd /path/to/Newsletter && python scripts/weekly_newsletter.py
```

### GitHub Actions (Recommended for Hosted Solutions)

Create `.github/workflows/newsletter.yml`:

```yaml
name: Weekly Newsletter

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  send-newsletter:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
    
    - name: Send Newsletter
      env:
        SMTP_EMAIL: ${{ secrets.SMTP_EMAIL }}
        SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
      run: |
        python scripts/weekly_newsletter.py
```

### Cloud Functions/Serverless

For serverless automation, you can deploy the newsletter script to:
- **Vercel Functions**
- **Netlify Functions**
- **AWS Lambda**
- **Google Cloud Functions**

## Step 6: Monitoring and Analytics

### Health Monitoring

1. **Uptime Monitoring**
   - Use services like UptimeRobot or Pingdom
   - Monitor both frontend and backend URLs

2. **Error Tracking**
   - Integrate Sentry for error tracking
   - Add to both frontend and backend

### Analytics

1. **Google Analytics**
   ```html
   <!-- Add to frontend/index.html -->
   <!-- Google tag (gtag.js) -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'GA_MEASUREMENT_ID');
   </script>
   ```

2. **Email Analytics**
   - Track open rates and click rates
   - Use email tracking pixels
   - Monitor bounce rates

## Security Considerations

### Environment Variables
- Never commit `.env` files
- Use platform-specific secret management
- Rotate API keys regularly

### Rate Limiting
- Implement rate limiting on subscription endpoints
- Use CAPTCHA for public forms
- Monitor for abuse

### Data Protection
- Implement GDPR compliance
- Provide data export functionality
- Secure database backups

## Performance Optimization

### Frontend
- Optimize images and assets
- Use CDN for static files
- Implement caching headers

### Backend
- Use connection pooling
- Implement API caching
- Optimize database queries

### Email Delivery
- Implement retry logic
- Use proper email authentication (SPF, DKIM)
- Monitor deliverability rates

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check `FRONTEND_URL` in backend environment
   - Verify CORS configuration in `main.py`

2. **Email Delivery Issues**
   - Verify Gmail App Password
   - Check spam folders
   - Test with different email providers

3. **Database Errors**
   - Check file permissions
   - Verify database path
   - Ensure persistent storage

4. **AI Generation Failures**
   - Verify API keys
   - Check rate limits
   - Test fallback content

### Debug Commands

```bash
# Test backend health
curl https://your-backend-url.com/health

# Test database connection
cd backend && python database.py

# Test email system
cd backend && python -c "from mailer.email_sender import EmailSender; EmailSender().test_smtp_connection()"

# Test AI generation
cd ai_agent && python content_generator.py
```

## Scaling Considerations

### Growing Subscriber Base
- Consider switching to PostgreSQL for better performance
- Implement email service provider (SendGrid, Mailgun)
- Use message queues for background processing

### High Availability
- Deploy to multiple regions
- Implement database replication
- Use load balancers

### Cost Optimization
- Monitor usage and costs
- Implement efficient batching
- Use spot instances for background jobs

## Backup and Recovery

### Database Backups
```bash
# Backup SQLite database
cp newsletter.db newsletter_backup_$(date +%Y%m%d).db

# Restore from backup
cp newsletter_backup_20240115.db newsletter.db
```

### Configuration Backups
- Backup environment configurations
- Document deployment procedures
- Version control all infrastructure code

## Legal Compliance

### Email Marketing Laws
- Implement proper unsubscribe mechanisms
- Include physical address in emails
- Follow CAN-SPAM Act guidelines
- Comply with GDPR for EU subscribers

### Privacy Policy
- Create comprehensive privacy policy
- Explain data collection and usage
- Provide data deletion procedures
- Include cookie policy if applicable

This deployment guide should help you successfully launch your AI Newsletter Platform in production!
