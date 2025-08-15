#!/usr/bin/env python3
"""
DataDispatch Platform Test Suite
Comprehensive testing of all platform components
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir / "backend"))
sys.path.insert(0, str(current_dir / "ai_agent"))
sys.path.insert(0, str(current_dir / "mailer"))


class TestReport:
    def __init__(self):
        self.tests = []
        self.start_time = time.time()

    def add_test(self, component, test_name, status, details="", duration=0.0):
        self.tests.append(
            {
                "component": component,
                "test_name": test_name,
                "status": status,  # "PASS", "FAIL", "SKIP"
                "details": details,
                "duration": duration,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )

    def print_progress(self, message):
        print(f"🔍 {message}")

    def generate_report(self):
        total_time = time.time() - self.start_time
        passed = len([t for t in self.tests if t["status"] == "PASS"])
        failed = len([t for t in self.tests if t["status"] == "FAIL"])
        skipped = len([t for t in self.tests if t["status"] == "SKIP"])

        report = f"""
# 📊 DataDispatch Platform Test Report
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Duration:** {total_time:.2f} seconds

## 📈 Summary
- **Total Tests:** {len(self.tests)}
- **✅ Passed:** {passed}
- **❌ Failed:** {failed}
- **⏭️ Skipped:** {skipped}
- **Success Rate:** {(passed/len(self.tests)*100):.1f}%

## 🧪 Test Results

"""

        components = {}
        for test in self.tests:
            comp = test["component"]
            if comp not in components:
                components[comp] = []
            components[comp].append(test)

        for component, tests in components.items():
            report += f"### {component}\n\n"
            for test in tests:
                status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}[test["status"]]
                report += f"- {status_icon} **{test['test_name']}** ({test['duration']:.2f}s)\n"
                if test["details"]:
                    report += f"  - {test['details']}\n"
                report += "\n"

        return report


def test_environment():
    """Test environment configuration"""
    report = TestReport()
    report.print_progress("Testing environment configuration...")

    start = time.time()
    try:
        from dotenv import load_dotenv

        load_dotenv()

        # Check critical env vars
        critical_vars = ["SMTP_EMAIL", "SMTP_PASSWORD"]
        missing = [var for var in critical_vars if not os.getenv(var)]

        if missing:
            report.add_test(
                "Environment",
                "Critical Environment Variables",
                "FAIL",
                f"Missing: {', '.join(missing)}",
                time.time() - start,
            )
        else:
            report.add_test(
                "Environment",
                "Critical Environment Variables",
                "PASS",
                "All critical variables present",
                time.time() - start,
            )

        # Check optional vars
        ai_provider = os.getenv("AI_PROVIDER", "ollama")
        ollama_model = os.getenv("OLLAMA_MODEL", "mistral:latest")
        report.add_test(
            "Environment",
            "AI Configuration",
            "PASS",
            f"Provider: {ai_provider}, Model: {ollama_model}",
            time.time() - start,
        )

    except Exception as e:
        report.add_test(
            "Environment", "Environment Loading", "FAIL", str(e), time.time() - start
        )

    return report


def test_database():
    """Test database functionality"""
    report = TestReport()
    report.print_progress("Testing database functionality...")

    try:
        from backend.database import SessionLocal, SubscriberDB, init_db

        # Test database initialization
        start = time.time()
        init_db()
        report.add_test(
            "Database",
            "Database Initialization",
            "PASS",
            "SQLite database created/connected",
            time.time() - start,
        )

        # Test database operations
        start = time.time()
        db = SessionLocal()
        subscriber_db = SubscriberDB(db)

        # Test subscriber operations
        test_email = f"test_{int(time.time())}@example.com"
        subscriber = subscriber_db.create_subscriber(test_email)
        report.add_test(
            "Database",
            "Create Subscriber",
            "PASS",
            f"Created subscriber: {subscriber.email}",
            time.time() - start,
        )

        # Test subscriber count
        start = time.time()
        stats = subscriber_db.get_subscriber_count()
        report.add_test(
            "Database",
            "Subscriber Statistics",
            "PASS",
            f"Active: {stats['active']}, Total: {stats['total']}",
            time.time() - start,
        )

        db.close()

    except Exception as e:
        report.add_test(
            "Database", "Database Operations", "FAIL", str(e), time.time() - start
        )

    return report


def test_api():
    """Test FastAPI backend"""
    report = TestReport()
    report.print_progress("Testing API endpoints...")

    base_url = "http://localhost:8000"

    # Test health endpoint
    start = time.time()
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            report.add_test(
                "API",
                "Health Endpoint",
                "PASS",
                f"Status: {response.status_code}",
                time.time() - start,
            )
        else:
            report.add_test(
                "API",
                "Health Endpoint",
                "FAIL",
                f"Status: {response.status_code}",
                time.time() - start,
            )
    except Exception as e:
        report.add_test("API", "Health Endpoint", "FAIL", str(e), time.time() - start)

    # Test subscription endpoint
    start = time.time()
    try:
        test_email = f"api_test_{int(time.time())}@example.com"
        response = requests.post(
            f"{base_url}/subscribe", json={"email": test_email}, timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                report.add_test(
                    "API",
                    "Subscribe Endpoint",
                    "PASS",
                    f"Subscribed: {test_email}",
                    time.time() - start,
                )
            else:
                report.add_test(
                    "API",
                    "Subscribe Endpoint",
                    "FAIL",
                    data.get("message", "Unknown error"),
                    time.time() - start,
                )
        else:
            report.add_test(
                "API",
                "Subscribe Endpoint",
                "FAIL",
                f"Status: {response.status_code}",
                time.time() - start,
            )
    except Exception as e:
        report.add_test(
            "API", "Subscribe Endpoint", "FAIL", str(e), time.time() - start
        )

    # Test stats endpoint
    start = time.time()
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            stats = data.get("subscriber_stats", {})
            report.add_test(
                "API",
                "Stats Endpoint",
                "PASS",
                f"Active: {stats.get('active', 0)}",
                time.time() - start,
            )
        else:
            report.add_test(
                "API",
                "Stats Endpoint",
                "FAIL",
                f"Status: {response.status_code}",
                time.time() - start,
            )
    except Exception as e:
        report.add_test("API", "Stats Endpoint", "FAIL", str(e), time.time() - start)

    return report


def test_ai_generation():
    """Test AI content generation"""
    report = TestReport()
    report.print_progress("Testing AI content generation...")

    try:
        from ai_agent.content_generator import ContentGenerator

        # Test AI connection
        start = time.time()
        generator = ContentGenerator()
        connections = generator.test_ai_connection()

        if connections.get("ollama"):
            report.add_test(
                "AI Generation",
                "Ollama Connection",
                "PASS",
                f"Model: {generator.ollama_model}",
                time.time() - start,
            )
        elif connections.get("openai"):
            report.add_test(
                "AI Generation",
                "OpenAI Connection",
                "PASS",
                "OpenAI API connected",
                time.time() - start,
            )
        else:
            report.add_test(
                "AI Generation",
                "AI Connection",
                "FAIL",
                "No AI services available",
                time.time() - start,
            )

        # Test content generation
        start = time.time()
        content = generator.generate_newsletter_content()

        if content.get("subject") and content.get("html"):
            subject_len = len(content["subject"])
            html_len = len(content["html"])
            report.add_test(
                "AI Generation",
                "Content Generation",
                "PASS",
                f"Subject: {subject_len} chars, HTML: {html_len} chars",
                time.time() - start,
            )
        else:
            report.add_test(
                "AI Generation",
                "Content Generation",
                "FAIL",
                "Invalid content structure",
                time.time() - start,
            )

    except Exception as e:
        report.add_test(
            "AI Generation",
            "AI Content Generation",
            "FAIL",
            str(e),
            time.time() - start,
        )

    return report


def test_email_system():
    """Test email functionality"""
    report = TestReport()
    report.print_progress("Testing email system...")

    try:
        from mailer.email_sender import EmailSender

        # Test SMTP connection
        start = time.time()
        sender = EmailSender()
        smtp_ok = sender.test_smtp_connection()

        if smtp_ok:
            report.add_test(
                "Email System",
                "SMTP Connection",
                "PASS",
                f"Connected to {sender.smtp_server}",
                time.time() - start,
            )

            # Test email sending
            start = time.time()
            email_sent = sender.send_test_email()
            if email_sent:
                report.add_test(
                    "Email System",
                    "Test Email Sending",
                    "PASS",
                    f"Sent to {sender.smtp_email}",
                    time.time() - start,
                )
            else:
                report.add_test(
                    "Email System",
                    "Test Email Sending",
                    "FAIL",
                    "Failed to send test email",
                    time.time() - start,
                )
        else:
            report.add_test(
                "Email System",
                "SMTP Connection",
                "FAIL",
                "SMTP connection failed",
                time.time() - start,
            )

    except Exception as e:
        report.add_test(
            "Email System", "Email Configuration", "FAIL", str(e), time.time() - start
        )

    return report


def test_frontend():
    """Test frontend files"""
    report = TestReport()
    report.print_progress("Testing frontend files...")

    frontend_files = [
        "frontend/index.html",
        "frontend/unsubscribe.html",
        "frontend/style.css",
        "frontend/script.js",
    ]

    for file_path in frontend_files:
        start = time.time()
        full_path = current_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            report.add_test(
                "Frontend",
                f"{file_path}",
                "PASS",
                f"Size: {size} bytes",
                time.time() - start,
            )
        else:
            report.add_test(
                "Frontend",
                f"{file_path}",
                "FAIL",
                "File not found",
                time.time() - start,
            )

    # Test for DataDispatch branding
    start = time.time()
    index_file = current_dir / "frontend/index.html"
    if index_file.exists():
        content = index_file.read_text()
        if "DataDispatch" in content:
            report.add_test(
                "Frontend",
                "DataDispatch Branding",
                "PASS",
                "Branding updated correctly",
                time.time() - start,
            )
        else:
            report.add_test(
                "Frontend",
                "DataDispatch Branding",
                "FAIL",
                "Old branding still present",
                time.time() - start,
            )

    return report


def test_automation_scripts():
    """Test automation scripts"""
    report = TestReport()
    report.print_progress("Testing automation scripts...")

    scripts = [
        "auto_update_newsletter.py",
        "generate_newsletter.sh",
        "scripts/weekly_newsletter.py",
    ]

    for script in scripts:
        start = time.time()
        script_path = current_dir / script
        if script_path.exists():
            if script.endswith(".py"):
                # Test Python syntax
                try:
                    with open(script_path, "r") as f:
                        compile(f.read(), script_path, "exec")
                    report.add_test(
                        "Automation",
                        f"{script}",
                        "PASS",
                        "Valid Python syntax",
                        time.time() - start,
                    )
                except SyntaxError as e:
                    report.add_test(
                        "Automation",
                        f"{script}",
                        "FAIL",
                        f"Syntax error: {e}",
                        time.time() - start,
                    )
            elif script.endswith(".sh"):
                # Check if executable
                if os.access(script_path, os.X_OK):
                    report.add_test(
                        "Automation",
                        f"{script}",
                        "PASS",
                        "Executable",
                        time.time() - start,
                    )
                else:
                    report.add_test(
                        "Automation",
                        f"{script}",
                        "FAIL",
                        "Not executable",
                        time.time() - start,
                    )
        else:
            report.add_test(
                "Automation", f"{script}", "FAIL", "File not found", time.time() - start
            )

    return report


def main():
    """Run all tests and generate report"""
    print("🚀 DataDispatch Platform Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    all_reports = []

    # Run all test suites
    test_suites = [
        test_environment,
        test_database,
        test_api,
        test_ai_generation,
        test_email_system,
        test_frontend,
        test_automation_scripts,
    ]

    for test_suite in test_suites:
        try:
            report = test_suite()
            all_reports.append(report)
        except Exception as e:
            print(f"❌ Error in {test_suite.__name__}: {e}")

    # Combine all reports
    master_report = TestReport()
    for report in all_reports:
        master_report.tests.extend(report.tests)

    # Generate final report
    final_report = master_report.generate_report()

    # Save to file
    report_file = (
        current_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    with open(report_file, "w") as f:
        f.write(final_report)

    print(final_report)
    print(f"📄 Full report saved to: {report_file}")


if __name__ == "__main__":
    main()
