import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Tuple
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailSender:
    def __init__(self):
        self.smtp_email = os.getenv("SMTP_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.from_name = os.getenv("NEWSLETTER_FROM_NAME", "DataDispatch")
        self.max_batch_size = 50  # Gmail's BCC limit

        if not self.smtp_email or not self.smtp_password:
            raise ValueError("SMTP credentials not configured. Check your .env file.")

    def send_newsletter(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        unsubscribe_base_url: str = "https://your-domain.com/unsubscribe",
    ) -> Dict:
        """
        Send newsletter to all recipients in batches

        Args:
            recipients: List of email addresses
            subject: Email subject line
            html_content: HTML email content
            unsubscribe_base_url: Base URL for unsubscribe links

        Returns:
            Dict with sending statistics
        """
        start_time = time.time()
        total_sent = 0
        total_failed = 0
        failed_emails = []

        print(f"📧 Starting newsletter send to {len(recipients)} recipients...")

        # Split recipients into batches
        batches = self._create_batches(recipients, self.max_batch_size)

        for i, batch in enumerate(batches):
            print(f"📨 Sending batch {i+1}/{len(batches)} ({len(batch)} recipients)...")

            try:
                batch_result = self._send_batch(
                    batch, subject, html_content, unsubscribe_base_url
                )
                total_sent += batch_result["sent"]
                total_failed += batch_result["failed"]
                failed_emails.extend(batch_result["failed_emails"])

                # Rate limiting: Wait between batches to respect Gmail limits
                if i < len(batches) - 1:  # Don't wait after the last batch
                    print("⏳ Waiting 2 seconds between batches...")
                    time.sleep(2)

            except Exception as e:
                print(f"❌ Batch {i+1} failed completely: {str(e)}")
                total_failed += len(batch)
                failed_emails.extend(batch)

        end_time = time.time()
        total_time = round(end_time - start_time, 2)

        # Calculate statistics
        success_rate = (total_sent / len(recipients)) * 100 if recipients else 0

        stats = {
            "total_recipients": len(recipients),
            "sent": total_sent,
            "failed": total_failed,
            "success_rate": round(success_rate, 2),
            "total_time_seconds": total_time,
            "failed_emails": failed_emails,
            "batches_processed": len(batches),
        }

        print(f"✅ Newsletter sending completed!")
        print(
            f"📊 Sent: {total_sent}, Failed: {total_failed}, Success Rate: {success_rate:.1f}%"
        )
        print(f"⏱️  Total time: {total_time}s")

        return stats

    def _create_batches(
        self, recipients: List[str], batch_size: int
    ) -> List[List[str]]:
        """Split recipients into batches of specified size"""
        batches = []
        for i in range(0, len(recipients), batch_size):
            batches.append(recipients[i : i + batch_size])
        return batches

    def _send_batch(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        unsubscribe_base_url: str,
    ) -> Dict:
        """Send email to a batch of recipients using BCC"""
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_email or "", self.smtp_password or "")

            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.smtp_email}>"
            message["Subject"] = subject
            message["Reply-To"] = self.smtp_email or ""

            # Add unsubscribe link to content
            unsubscribe_link = f"{unsubscribe_base_url}?email={{email}}"
            final_html = html_content.replace("{{UNSUBSCRIBE_LINK}}", unsubscribe_link)

            # Create HTML part
            html_part = MIMEText(final_html, "html")
            message.attach(html_part)

            # Send to batch using BCC
            message["To"] = self.smtp_email or ""  # Send to self as primary recipient

            # Convert message to string
            text = message.as_string()

            # Send with BCC
            all_recipients = [self.smtp_email or ""] + recipients
            server.sendmail(self.smtp_email or "", all_recipients, text)

            server.quit()

            return {"sent": len(recipients), "failed": 0, "failed_emails": []}

        except Exception as e:
            print(f"❌ Batch sending failed: {str(e)}")
            return {"sent": 0, "failed": len(recipients), "failed_emails": recipients}

    def send_single_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        unsubscribe_url: str | None = None,
    ) -> bool:
        """
        Send a single email (useful for testing or transactional emails)

        Args:
            recipient: Email address
            subject: Email subject
            html_content: HTML content
            unsubscribe_url: Optional unsubscribe URL

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_email or "", self.smtp_password or "")

            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.smtp_email}>"
            message["To"] = recipient
            message["Subject"] = subject
            message["Reply-To"] = self.smtp_email or ""

            # Add unsubscribe link if provided
            if unsubscribe_url:
                final_html = html_content.replace(
                    "{{UNSUBSCRIBE_LINK}}", unsubscribe_url
                )
            else:
                final_html = html_content.replace("{{UNSUBSCRIBE_LINK}}", "#")

            # Create HTML part
            html_part = MIMEText(final_html, "html")
            message.attach(html_part)

            # Send email
            server.sendmail(self.smtp_email or "", [recipient], message.as_string())
            server.quit()

            print(f"✅ Email sent successfully to {recipient}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email to {recipient}: {str(e)}")
            return False

    def test_smtp_connection(self) -> bool:
        """Test SMTP connection and credentials"""
        try:
            print("🔌 Testing SMTP connection...")

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_email or "", self.smtp_password or "")
            server.quit()

            print("✅ SMTP connection successful!")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication failed. Check your email and password.")
            print(
                "💡 Make sure you're using a Gmail App Password, not your regular password."
            )
            return False
        except smtplib.SMTPConnectError:
            print(
                "❌ Could not connect to SMTP server. Check your internet connection."
            )
            return False
        except Exception as e:
            print(f"❌ SMTP connection failed: {str(e)}")
            return False

    def send_test_email(self) -> bool:
        """Send a test email to the configured email address"""
        if not self.test_smtp_connection():
            return False

        test_subject = "🧪 DataDispatch Platform Test Email"
        test_html = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px;">
                <h1>🧪 Test Email</h1>
                <p>This is a test email from your DataDispatch Platform!</p>
            </div>
            
            <div style="padding: 30px 0;">
                <h2>✅ SMTP Configuration Working!</h2>
                <p>If you received this email, your SMTP settings are configured correctly.</p>
                
                <p><strong>Configuration Details:</strong></p>
                <ul>
                    <li>SMTP Server: smtp.gmail.com</li>
                    <li>Port: 587</li>
                    <li>From: {from_name}</li>
                    <li>Timestamp: {timestamp}</li>
                </ul>
                
                <p>You can now send newsletters to your subscribers!</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-top: 20px;">
                <p style="margin: 0; font-size: 14px; color: #666;">
                    This is a test email from your DataDispatch Platform.<br>
                    <a href="{{UNSUBSCRIBE_LINK}}">Unsubscribe</a>
                </p>
            </div>
        </body>
        </html>
        """.format(
            from_name=self.from_name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        )

        return self.send_single_email(
            recipient=self.smtp_email or "",
            subject=test_subject,
            html_content=test_html,
            unsubscribe_url="https://your-domain.com/unsubscribe",
        )


def main():
    """Test the email sender"""
    print("📧 Testing Email Sender...")

    try:
        sender = EmailSender()

        # Test SMTP connection
        if sender.test_smtp_connection():
            # Send test email
            sender.send_test_email()

    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}")
        print("💡 Make sure to set SMTP_EMAIL and SMTP_PASSWORD in your .env file")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
