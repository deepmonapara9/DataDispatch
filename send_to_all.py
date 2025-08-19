#!/usr/bin/env python3
"""
Send custom newsletter to all subscribers
Usage: python send_to_all.py [--subject "Custom Subject"] [--generate-content]
"""

import sys
import os
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir / "backend"))
sys.path.insert(0, str(current_dir / "ai_agent"))
sys.path.insert(0, str(current_dir / "mailer"))

from backend.database import init_db, SubscriberDB, get_db
from mailer.email_sender import EmailSender
from ai_agent.content_generator import ContentGenerator
import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Send newsletter to all subscribers")
    parser.add_argument(
        "--subject", default="DataDispatch Newsletter", help="Email subject"
    )
    parser.add_argument(
        "--generate-content", action="store_true", help="Generate fresh AI content"
    )
    parser.add_argument("--file", help="Use content from HTML file")

    args = parser.parse_args()

    print(f"📧 DataDispatch Mass Email Sender")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Initialize database
    print("💾 Connecting to database...")
    # Change to backend directory to use the existing backend/newsletter.db
    import os
    original_cwd = os.getcwd()
    os.chdir('backend')
    init_db()
    
    # Get subscribers (while still in backend directory)
    print("👥 Fetching subscribers...")
    db_session = next(get_db())
    db = SubscriberDB(db_session)
    subscribers = db.get_active_subscribers()
    
    if not subscribers:
        print("❌ No active subscribers found!")
        os.chdir(original_cwd)  # Change back before returning
        return

    print(f"📊 Found {len(subscribers)} active subscribers")
    
    # Change back to original directory for the rest of the operations
    os.chdir(original_cwd)

    # Get content
    if args.generate_content:
        print("🤖 Generating fresh AI content...")
        generator = ContentGenerator()
        content = generator.generate_newsletter_content()
        subject = content.get("subject", args.subject)
        html_content = content.get("html", "")
    elif args.file:
        print(f"📄 Loading content from {args.file}...")
        with open(args.file, "r") as f:
            html_content = f.read()
        subject = args.subject
    else:
        # Use sample content
        print("📄 Using sample newsletter content...")
        from ai_agent.prompts import SAMPLE_NEWSLETTER_CONTENT

        html_content = SAMPLE_NEWSLETTER_CONTENT["html"]
        subject = args.subject

    # Send emails
    print(f"📧 Sending newsletter: '{subject}'")
    print(f"📄 Content length: {len(html_content)} characters")

    sender = EmailSender()
    emails = [sub.email for sub in subscribers]

    success = sender.send_newsletter(
        recipients=emails,
        subject=subject or "DataDispatch Newsletter",
        html_content=html_content,
        unsubscribe_base_url="http://localhost:3000/unsubscribe.html",
    )

    if success:
        print("✅ Newsletter sent successfully to all subscribers!")
    else:
        print("❌ Failed to send newsletter")

    # Close database session
    db_session.close()


if __name__ == "__main__":
    main()
