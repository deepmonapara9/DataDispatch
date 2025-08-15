#!/usr/bin/env python3
"""
DataDispatch Auto-Update Newsletter Script

This script automatically:
1. Generates fresh newsletter content using your LLM
2. Updates the sample_newsletter.html file with the new content
3. Optionally opens the updated file in browser

Usage:
  python auto_update_newsletter.py
  python auto_update_newsletter.py --watch  # Continuous generation every 5 minutes
  python auto_update_newsletter.py --open   # Open in browser after generation
"""

import os
import sys
import time
import shutil
import argparse
import webbrowser
from pathlib import Path
from datetime import datetime

# Add project paths for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir / "ai_agent"))

try:
    from ai_agent.content_generator import ContentGenerator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running this from the project root directory")
    sys.exit(1)


def generate_and_update_newsletter(open_browser=False):
    """Generate new content and update sample_newsletter.html"""

    print("🤖 Generating fresh newsletter content...")
    start_time = time.time()

    try:
        # Generate content using LLM
        generator = ContentGenerator()
        content = generator.generate_newsletter_content()

        generation_time = round(time.time() - start_time, 2)

        print(f"✅ Content generated in {generation_time}s")
        print(f"📧 Subject: {content['subject']}")
        print(f"📄 HTML length: {len(content['html'])} characters")

        # Save to project's sample_newsletter.html
        sample_file = current_dir / "sample_newsletter.html"

        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(content["html"])

        print(f"📝 Updated: {sample_file}")

        # Also save a timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = current_dir / f"newsletter_backup_{timestamp}.html"

        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(content["html"])

        print(f"💾 Backup saved: {backup_file}")

        # Open in browser if requested
        if open_browser:
            file_url = f"file://{sample_file.absolute()}"
            webbrowser.open(file_url)
            print(f"🌐 Opened in browser: {file_url}")

        return True

    except Exception as e:
        print(f"❌ Error generating content: {str(e)}")
        return False


def watch_mode():
    """Continuously generate content every 5 minutes"""
    print("👀 Watch mode enabled - generating fresh content every 5 minutes")
    print("Press Ctrl+C to stop")

    try:
        while True:
            generate_and_update_newsletter()
            print("\n⏰ Waiting 5 minutes for next generation...")
            time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        print("\n🛑 Watch mode stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Auto-update newsletter with fresh LLM content"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously generate content every 5 minutes",
    )
    parser.add_argument(
        "--open", action="store_true", help="Open updated file in browser"
    )

    args = parser.parse_args()

    print("🚀 DataDispatch Newsletter Auto-Updater")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if args.watch:
        watch_mode()
    else:
        success = generate_and_update_newsletter(open_browser=args.open)
        if success:
            print("\n✅ Newsletter updated successfully!")
            print("💡 Use --open to auto-open in browser")
            print("💡 Use --watch for continuous updates")
        else:
            print("\n❌ Failed to update newsletter")
            sys.exit(1)


if __name__ == "__main__":
    main()
