#!/usr/bin/env python3
"""
Weekly Newsletter Automation Script

This script:
1. Generates AI-powered newsletter content
2. Fetches active subscribers from database
3. Sends newsletter to all subscribers
4. Logs the sending statistics

Run this script with cron for automated weekly newsletters:
0 9 * * 1 cd /path/to/Newsletter && python scripts/weekly_newsletter.py
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "ai_agent"))
sys.path.insert(0, str(project_root / "mailer"))

try:
    from backend.database import SessionLocal, SubscriberDB, SendLogDB, init_db
    from ai_agent.content_generator import ContentGenerator
    from mailer.email_sender import EmailSender
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running this script from the project root directory")
    print("💡 Install required packages: pip install -r backend/requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()


def setup_logging():
    """Setup basic logging"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    class Logger:
        def __init__(self, filename):
            self.filename = filename
            self.console = True

        def log(self, message):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] {message}"

            if self.console:
                print(log_message)

            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")

    return Logger(log_file)


def get_active_subscribers(db_session):
    """Get all active subscribers"""
    try:
        subscriber_db = SubscriberDB(db_session)
        subscribers = subscriber_db.get_active_subscribers()

        return [sub.email for sub in subscribers]
    except Exception as e:
        raise Exception(f"Failed to fetch subscribers: {str(e)}")


def generate_newsletter_content():
    """Generate newsletter content using AI"""
    try:
        generator = ContentGenerator()
        content = generator.generate_newsletter_content()

        if not content.get("subject") or not content.get("html"):
            raise Exception("Generated content is missing subject or HTML")

        return content
    except Exception as e:
        raise Exception(f"Failed to generate content: {str(e)}")


def send_newsletter_to_subscribers(recipients, subject, html_content):
    """Send newsletter to all recipients"""
    try:
        sender = EmailSender()

        # Get unsubscribe base URL from environment or use default
        frontend_url = os.getenv("FRONTEND_URL", "https://your-domain.com")
        unsubscribe_url = f"{frontend_url}/unsubscribe.html"

        stats = sender.send_newsletter(
            recipients=recipients,
            subject=subject,
            html_content=html_content,
            unsubscribe_base_url=unsubscribe_url,
        )

        return stats
    except Exception as e:
        raise Exception(f"Failed to send newsletter: {str(e)}")


def log_sending_statistics(db_session, stats, subject, error_details=None):
    """Log sending statistics to database"""
    try:
        send_log_db = SendLogDB(db_session)

        send_log_db.create_send_log(
            sent_count=stats.get("sent", 0),
            failures=stats.get("failed", 0),
            latency_ms=int(stats.get("total_time_seconds", 0) * 1000),
            error_details=error_details,
            newsletter_subject=subject,
        )
    except Exception as e:
        print(f"⚠️  Warning: Failed to log statistics: {str(e)}")


def validate_environment():
    """Validate required environment variables"""
    required_vars = ["SMTP_EMAIL", "SMTP_PASSWORD"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        raise Exception(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


def main():
    """Main newsletter sending function"""
    logger = setup_logging()
    start_time = time.time()

    logger.log("🚀 Starting weekly newsletter automation...")

    try:
        # Validate environment
        logger.log("🔍 Validating environment configuration...")
        validate_environment()

        # Initialize database
        logger.log("💾 Initializing database connection...")
        # Change to backend directory to use backend/newsletter.db
        original_cwd = os.getcwd()
        os.chdir(str(project_root / "backend"))
        init_db()
        db_session = SessionLocal()

        try:
            # Get active subscribers (while in backend directory)
            logger.log("👥 Fetching active subscribers...")
            recipients = get_active_subscribers(db_session)

            if not recipients:
                logger.log("⚠️  No active subscribers found. Exiting.")
                return

            logger.log(f"📊 Found {len(recipients)} active subscribers")

            # Change back to original directory for content generation
            os.chdir(original_cwd)

            # Generate newsletter content
            logger.log("🤖 Generating newsletter content with AI...")
            content = generate_newsletter_content()

            logger.log(f"📝 Generated content: '{content['subject']}'")
            logger.log(f"📄 HTML content length: {len(content['html'])} characters")

            # Send newsletter
            logger.log("📧 Sending newsletter to subscribers...")
            stats = send_newsletter_to_subscribers(
                recipients=recipients,
                subject=content["subject"],
                html_content=content["html"],
            )

            # Log statistics
            logger.log("📊 Logging sending statistics...")
            error_details = None
            if stats.get("failed_emails"):
                error_details = f"Failed emails: {', '.join(stats['failed_emails'])}"

            log_sending_statistics(
                db_session=db_session,
                stats=stats,
                subject=content["subject"],
                error_details=error_details,
            )

            # Summary
            end_time = time.time()
            total_time = round(end_time - start_time, 2)

            logger.log("✅ Newsletter automation completed successfully!")
            logger.log(f"📊 Summary:")
            logger.log(f"   • Total recipients: {stats['total_recipients']}")
            logger.log(f"   • Successfully sent: {stats['sent']}")
            logger.log(f"   • Failed: {stats['failed']}")
            logger.log(f"   • Success rate: {stats['success_rate']:.1f}%")
            logger.log(f"   • Total time: {total_time}s")

            if stats.get("failed_emails"):
                logger.log(f"⚠️  Failed recipients: {', '.join(stats['failed_emails'])}")

        finally:
            db_session.close()

    except Exception as e:
        logger.log(f"❌ Newsletter automation failed: {str(e)}")

        # Try to log the error if database is available
        try:
            db_session = SessionLocal()
            log_sending_statistics(
                db_session=db_session,
                stats={"sent": 0, "failed": 0, "total_time_seconds": 0},
                subject="Newsletter Generation Failed",
                error_details=str(e),
            )
            db_session.close()
        except:
            pass  # If we can't log to database, just continue

        # Exit with error code for cron monitoring
        sys.exit(1)


def test_newsletter_system():
    """Test the entire newsletter system without sending to all subscribers"""
    logger = setup_logging()

    logger.log("🧪 Testing newsletter system...")

    try:
        # Validate environment
        validate_environment()

        # Test database connection
        logger.log("💾 Testing database connection...")
        init_db()
        db_session = SessionLocal()

        subscriber_db = SubscriberDB(db_session)
        stats = subscriber_db.get_subscriber_count()
        logger.log(f"📊 Database OK - Active subscribers: {stats['active']}")

        # Test AI content generation
        logger.log("🤖 Testing AI content generation...")
        generator = ContentGenerator()
        content = generator.generate_newsletter_content()
        logger.log(f"✅ AI generation OK - Subject: '{content['subject']}'")

        # Test email system
        logger.log("📧 Testing email system...")
        sender = EmailSender()
        if sender.test_smtp_connection():
            logger.log("✅ SMTP connection OK")

            # Send test email to configured email address
            if sender.smtp_email:
                test_success = sender.send_single_email(
                    recipient=sender.smtp_email,
                    subject="🧪 Newsletter System Test",
                    html_content=content["html"],
                    unsubscribe_url="https://your-domain.com/unsubscribe",
                )
            else:
                logger.log("❌ No SMTP email configured for test")
                test_success = False

            if test_success:
                logger.log("✅ Test email sent successfully!")
            else:
                logger.log("❌ Test email failed")

        db_session.close()
        logger.log("✅ Newsletter system test completed!")

    except Exception as e:
        logger.log(f"❌ Newsletter system test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_newsletter_system()
    else:
        main()
