# AI Prompts for Newsletter Content Generation

NEWSLETTER_SYSTEM_PROMPT = """
You are an AI assistant that generates high-quality newsletter content for DataDispatch, 
a tech-focused publication. Your goal is to create engaging, informative, and well-structured 
newsletters about AI, technology, and developer tools.

Guidelines:
1. Focus on the latest developments in AI, machine learning, developer tools, and emerging technologies
2. Write in a professional yet conversational tone
3. Keep content concise but informative
4. Include actionable insights and practical information
5. Structure content in clear sections with emojis for visual appeal
6. Always provide value to developers and tech professionals

Output Format:
- Return ONLY valid JSON with exactly two keys: "subject" and "html"
- The "subject" should be compelling and SEO-friendly (max 60 characters)
- The "html" should be a complete HTML email template with inline CSS for email compatibility
- Include unsubscribe link placeholder: {{UNSUBSCRIBE_LINK}}
- Make it mobile-friendly and accessible
"""

NEWSLETTER_CONTENT_PROMPT = """
Generate a comprehensive weekly newsletter for DataDispatch readers - tech professionals and developers. 

Content should include:
1. 🔥 This Week's Hot Topics (3-4 latest AI/tech developments)
2. 🛠️ Tools & Resources (2-3 new developer tools or resources)
3. 📚 Learning & Insights (educational content, tutorials, or industry insights)
4. 🚀 Quick Wins (actionable tips developers can implement immediately)

Topics to potentially cover:
- Latest AI model releases and capabilities
- New JavaScript/Python frameworks or libraries
- Developer productivity tools
- Cloud computing updates
- Cybersecurity developments
- Open source project highlights
- Industry trends and predictions
- Programming best practices

Current date: {current_date}

Make sure the content is:
- Up-to-date and relevant
- Valuable for developers and tech professionals
- Well-structured with clear sections
- Engaging but professional
- Mobile-friendly HTML with inline CSS

Return ONLY valid JSON with "subject" and "html" keys.
"""

HTML_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; }}
        .content {{ padding: 30px 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 15px; display: flex; align-items: center; }}
        .section-content {{ color: #374151; line-height: 1.6; }}
        .item {{ margin-bottom: 20px; padding: 15px; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #667eea; }}
        .item-title {{ font-weight: 600; color: #1f2937; margin-bottom: 8px; }}
        .item-description {{ color: #4b5563; }}
        .link {{ color: #667eea; text-decoration: none; font-weight: 500; }}
        .footer {{ background-color: #f8fafc; padding: 30px 20px; text-align: center; color: #6b7280; font-size: 14px; }}
        .unsubscribe {{ margin-top: 20px; }}
        .unsubscribe a {{ color: #9ca3af; text-decoration: none; }}
        @media only screen and (max-width: 600px) {{
            .container {{ width: 100% !important; }}
            .header, .content, .footer {{ padding: 20px 15px !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; font-size: 24px;">📊 DataDispatch</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">{subject}</p>
        </div>
        
        <div class="content">
            {content_sections}
        </div>
        
        <div class="footer">
            <p>Thank you for reading! Stay ahead in AI & Technology.</p>
            <p style="margin-top: 20px;">
                <strong>DataDispatch</strong><br>
                Curated insights for developers and tech professionals
            </p>
            <div class="unsubscribe">
                <p>
                    <a href="{{{{UNSUBSCRIBE_LINK}}}}">Unsubscribe</a> | 
                    <a href="mailto:contact@your-domain.com">Contact Us</a>
                </p>
                <p style="margin-top: 10px; font-size: 12px; color: #9ca3af;">
                    You received this email because you subscribed to our newsletter.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""

OLLAMA_SYSTEM_PROMPT = """
You are a DataDispatch tech newsletter curator. Generate engaging newsletter content about AI, programming, and technology trends. 
Return only valid JSON with 'subject' and 'html' keys. The HTML should be email-ready with inline CSS.
Keep the subject under 60 characters and make the content valuable for developers.
"""

SAMPLE_NEWSLETTER_CONTENT = {
    "subject": "🚀 AI Breakthroughs & Dev Tools You Need This Week",
    "html": """
    <div class="section">
        <h2 class="section-title">🔥 This Week's Hot Topics</h2>
        <div class="section-content">
            <div class="item">
                <div class="item-title">GPT-4 Turbo with Vision Now Available</div>
                <div class="item-description">
                    OpenAI released GPT-4 Turbo with enhanced vision capabilities and lower costs. 
                    Perfect for developers building multimodal applications.
                    <a href="#" class="link">Learn more →</a>
                </div>
            </div>
            <div class="item">
                <div class="item-title">React 18.3 Released with New Hooks</div>
                <div class="item-description">
                    The latest React update brings performance improvements and new experimental hooks 
                    for better state management.
                    <a href="#" class="link">Read changelog →</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">🛠️ Tools & Resources</h2>
        <div class="section-content">
            <div class="item">
                <div class="item-title">Cursor - AI-Powered Code Editor</div>
                <div class="item-description">
                    A VS Code alternative with built-in AI assistance for faster coding. 
                    Free for personal use with GitHub Copilot integration.
                    <a href="#" class="link">Try it free →</a>
                </div>
            </div>
            <div class="item">
                <div class="item-title">shadcn/ui - Beautiful UI Components</div>
                <div class="item-description">
                    Copy-paste React components built with Tailwind CSS and Radix UI. 
                    Perfect for rapid prototyping.
                    <a href="#" class="link">Explore components →</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">📚 Learning & Insights</h2>
        <div class="section-content">
            <div class="item">
                <div class="item-title">System Design Interview Guide 2024</div>
                <div class="item-description">
                    Complete guide covering scalability, databases, caching, and microservices 
                    with real-world examples from FAANG companies.
                    <a href="#" class="link">Read guide →</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">🚀 Quick Wins</h2>
        <div class="section-content">
            <div class="item">
                <div class="item-title">Speed up Docker builds by 50%</div>
                <div class="item-description">
                    Use multi-stage builds and .dockerignore to reduce build times. 
                    Simple optimization that every developer should know.
                    <a href="#" class="link">See examples →</a>
                </div>
            </div>
        </div>
    </div>
    """,
}
