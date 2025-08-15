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
1. This Week's Highlights (3-4 latest AI/tech developments)
2. Tools & Resources (2-3 new developer tools or resources)
3. Learning (educational content, tutorials, or industry insights)
4. Quick Tips (actionable tips developers can implement immediately)

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

Design Guidelines:
- Use a minimal, clean aesthetic without flashy elements
- No emojis in section titles - keep it professional
- Clean typography with subtle visual hierarchy
- Separated sections with simple dividers
- Focus on content over decoration
- Maintain excellent readability

Make sure the content is:
- Up-to-date and relevant
- Valuable for developers and tech professionals
- Well-structured with clear sections
- Professional and minimal in design
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
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background-color: #ffffff; color: #374151; }}
        .container {{ max-width: 580px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #e5e7eb; }}
        .logo {{ font-size: 20px; font-weight: 700; color: #111827; margin: 0; letter-spacing: -0.025em; }}
        .subject {{ font-size: 14px; color: #6b7280; margin: 8px 0 0 0; font-weight: 400; }}
        .content {{ line-height: 1.7; }}
        .section {{ margin-bottom: 36px; }}
        .section-title {{ font-size: 16px; font-weight: 600; color: #111827; margin: 0 0 16px 0; }}
        .item {{ margin-bottom: 24px; }}
        .item-title {{ font-size: 15px; font-weight: 500; color: #111827; margin: 0 0 6px 0; }}
        .item-description {{ font-size: 14px; color: #4b5563; line-height: 1.6; margin: 0; }}
        .link {{ color: #2563eb; text-decoration: none; border-bottom: 1px solid transparent; }}
        .link:hover {{ border-bottom-color: #2563eb; }}
        .divider {{ height: 1px; background-color: #f3f4f6; margin: 32px 0; border: none; }}
        .footer {{ margin-top: 48px; padding-top: 24px; border-top: 1px solid #e5e7eb; text-align: center; }}
        .footer-content {{ font-size: 13px; color: #6b7280; line-height: 1.5; }}
        .footer-brand {{ font-weight: 600; color: #111827; }}
        .footer-links {{ margin-top: 16px; }}
        .footer-links a {{ color: #6b7280; text-decoration: none; font-size: 13px; margin: 0 8px; }}
        .footer-links a:hover {{ color: #374151; }}
        .footer-note {{ margin-top: 16px; font-size: 12px; color: #9ca3af; }}
        @media only screen and (max-width: 600px) {{
            .container {{ padding: 24px 16px; }}
            .section {{ margin-bottom: 28px; }}
            .item {{ margin-bottom: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">DataDispatch</h1>
            <p class="subject">{subject}</p>
        </div>
        
        <div class="content">
            {content_sections}
        </div>
        
        <div class="footer">
            <div class="footer-content">
                <p class="footer-brand">DataDispatch</p>
                <p>Curated insights for developers and tech professionals</p>
            </div>
            <div class="footer-links">
                <a href="{{{{UNSUBSCRIBE_LINK}}}}">Unsubscribe</a>
                <a href="mailto:contact@datadispatch.com">Contact</a>
            </div>
            <div class="footer-note">
                <p>You received this email because you subscribed to our newsletter.</p>
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
    "subject": "AI Breakthroughs & Dev Tools You Need This Week",
    "html": """
    <div class="section">
        <h2 class="section-title">This Week's Highlights</h2>
        <div class="item">
            <div class="item-title">GPT-4 Turbo with Enhanced Vision</div>
            <div class="item-description">
                OpenAI released GPT-4 Turbo with improved vision capabilities and reduced costs. 
                Ideal for developers building multimodal applications.
                <a href="#" class="link">Learn more</a>
            </div>
        </div>
        <div class="item">
            <div class="item-title">React 18.3 Performance Updates</div>
            <div class="item-description">
                Latest React update introduces performance improvements and experimental hooks 
                for enhanced state management.
                <a href="#" class="link">View changelog</a>
            </div>
        </div>
    </div>
    
    <hr class="divider">
    
    <div class="section">
        <h2 class="section-title">Tools & Resources</h2>
        <div class="item">
            <div class="item-title">Cursor AI Code Editor</div>
            <div class="item-description">
                VS Code alternative with integrated AI assistance for faster development. 
                Free for personal use with GitHub Copilot support.
                <a href="#" class="link">Try it free</a>
            </div>
        </div>
        <div class="item">
            <div class="item-title">shadcn/ui Component Library</div>
            <div class="item-description">
                Copy-paste React components built with Tailwind CSS and Radix UI. 
                Perfect for rapid prototyping and consistent design.
                <a href="#" class="link">Browse components</a>
            </div>
        </div>
    </div>
    
    <hr class="divider">
    
    <div class="section">
        <h2 class="section-title">Learning</h2>
        <div class="item">
            <div class="item-title">System Design Interview Guide 2024</div>
            <div class="item-description">
                Comprehensive guide covering scalability, databases, caching, and microservices 
                with practical examples from leading tech companies.
                <a href="#" class="link">Read guide</a>
            </div>
        </div>
    </div>
    
    <hr class="divider">
    
    <div class="section">
        <h2 class="section-title">Quick Tips</h2>
        <div class="item">
            <div class="item-title">Optimize Docker Build Performance</div>
            <div class="item-description">
                Use multi-stage builds and .dockerignore to reduce build times by up to 50%. 
                Essential optimization every developer should implement.
                <a href="#" class="link">View examples</a>
            </div>
        </div>
    </div>
    """,
}
