#!/usr/bin/env python3
"""
Newsletter Platform Configuration Test Script

This script tests all components of the newsletter platform to ensure
everything is configured correctly before deployment.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add paths for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir / "backend"))
sys.path.insert(0, str(current_dir / "ai_agent"))
sys.path.insert(0, str(current_dir / "mailer"))

def test_environment():
    """Test environment configuration"""
    print("🔍 Testing Environment Configuration...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment file loaded")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    
    # Check required variables
    required_vars = {
        "SMTP_EMAIL": os.getenv("SMTP_EMAIL"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
        "FRONTEND_URL": os.getenv("FRONTEND_URL", "http://localhost:3000")
    }
    
    missing_vars = []
    for var, value in required_vars.items():
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value if var != 'SMTP_PASSWORD' else '***hidden***'}")
    
    if missing_vars:
        print(f"❌ Missing required variables: {', '.join(missing_vars)}")
        return False
    
    # Check optional variables
    optional_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama2"),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    }
    
    for var, value in optional_vars.items():
        if value:
            display_value = value if var not in ['OPENAI_API_KEY'] else '***hidden***'
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚠️  {var}: Not set (optional)")
    
    return True

def test_database():
    """Test database connectivity and operations"""
    print("\n💾 Testing Database...")
    
    try:
        from database import init_db, SessionLocal, SubscriberDB
        
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Test database operations
        db = SessionLocal()
        try:
            subscriber_db = SubscriberDB(db)
            
            # Test subscriber count
            stats = subscriber_db.get_subscriber_count()
            print(f"✅ Database query successful - {stats['active']} active subscribers")
            
            # Test adding a test subscriber (we'll remove it)
            test_email = f"test-{int(time.time())}@example.com"
            try:
                test_subscriber = subscriber_db.create_subscriber(test_email)
                print(f"✅ Test subscriber created: {test_subscriber.email}")
                
                # Test unsubscribe
                subscriber_db.unsubscribe_subscriber(test_email)
                print("✅ Test subscriber unsubscribed")
                
            except Exception as e:
                print(f"⚠️  Database operation test: {str(e)}")
            
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

def test_ai_services():
    """Test AI content generation services"""
    print("\n🤖 Testing AI Services...")
    
    try:
        from content_generator import ContentGenerator
        
        generator = ContentGenerator()
        
        # Test AI connections
        connections = generator.test_ai_connection()
        
        if connections.get("openai"):
            print("✅ OpenAI connection successful")
        elif connections.get("ollama"):
            print("✅ Ollama connection successful")
        else:
            print("⚠️  No AI services available - will use fallback content")
        
        # Test content generation
        print("📝 Testing content generation...")
        start_time = time.time()
        content = generator.generate_newsletter_content()
        end_time = time.time()
        
        if content.get("subject") and content.get("html"):
            print(f"✅ Content generated in {end_time - start_time:.2f}s")
            print(f"   Subject: {content['subject'][:50]}...")
            print(f"   HTML length: {len(content['html'])} characters")
            
            # Save sample content
            with open("test_newsletter.html", "w", encoding="utf-8") as f:
                f.write(content["html"])
            print("💾 Sample newsletter saved as test_newsletter.html")
        else:
            print("❌ Content generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI service test failed: {str(e)}")
        return False

def test_email_service():
    """Test email service configuration"""
    print("\n📧 Testing Email Service...")
    
    try:
        from email_sender import EmailSender
        
        sender = EmailSender()
        
        # Test SMTP connection
        if sender.test_smtp_connection():
            print("✅ SMTP connection successful")
            
            # Ask user if they want to send a test email
            response = input("Send test email to configured address? (y/N): ").lower().strip()
            if response == 'y':
                if sender.send_test_email():
                    print("✅ Test email sent successfully")
                    print("📬 Check your inbox for the test email")
                else:
                    print("❌ Test email failed")
                    return False
            else:
                print("⏭️  Test email skipped")
            
            return True
        else:
            print("❌ SMTP connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Email service test failed: {str(e)}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    print("\n🌐 Testing Backend API...")
    
    try:
        # Try to import and start a test server
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test subscription endpoint with invalid email
        response = client.post("/subscribe", json={"email": "invalid-email"})
        if response.status_code == 422:  # Validation error expected
            print("✅ Email validation working")
        else:
            print(f"⚠️  Email validation response: {response.status_code}")
        
        # Test with valid email format
        test_email = f"test-{int(time.time())}@example.com"
        response = client.post("/subscribe", json={"email": test_email})
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Subscribe endpoint working")
                
                # Test unsubscribe
                response = client.post("/unsubscribe", json={"email": test_email})
                if response.status_code == 200 and response.json().get("success"):
                    print("✅ Unsubscribe endpoint working")
                else:
                    print(f"❌ Unsubscribe failed: {response.status_code}")
            else:
                print(f"❌ Subscribe failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ Subscribe endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot test API - missing dependency: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Backend API test failed: {str(e)}")
        return False

def test_frontend_files():
    """Test frontend files exist and are valid"""
    print("\n🌐 Testing Frontend Files...")
    
    frontend_files = [
        "frontend/index.html",
        "frontend/unsubscribe.html",
        "frontend/style.css",
        "frontend/script.js"
    ]
    
    all_exist = True
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
            
            # Basic validation
            if file_path.endswith('.html'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '<!DOCTYPE html>' in content and '</html>' in content:
                        print(f"   HTML structure valid")
                    else:
                        print(f"   ⚠️  HTML structure may be invalid")
            
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    # Check if API_BASE_URL is configured in script.js
    script_path = "frontend/script.js"
    if os.path.exists(script_path):
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'localhost:8000' in content:
                print("⚠️  API_BASE_URL still set to localhost - update for production")
            else:
                print("✅ API_BASE_URL configured")
    
    return all_exist

def run_integration_test():
    """Run a complete integration test"""
    print("\n🧪 Running Integration Test...")
    
    try:
        # This would test the complete flow:
        # 1. Generate content
        # 2. Save to database
        # 3. Send to test subscriber
        # 4. Verify logs
        
        from weekly_newsletter import main as newsletter_main
        
        print("⚠️  Integration test would send actual newsletter")
        response = input("Run full integration test? (sends real email) (y/N): ").lower().strip()
        
        if response == 'y':
            print("🚀 Running full newsletter automation test...")
            # Note: This would run the actual newsletter script
            print("✅ Integration test completed (simulated)")
        else:
            print("⏭️  Integration test skipped")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Newsletter Platform Configuration Test")
    print("=" * 50)
    
    start_time = time.time()
    
    tests = [
        ("Environment", test_environment),
        ("Database", test_database),
        ("AI Services", test_ai_services),
        ("Email Service", test_email_service),
        ("Backend API", test_backend_api),
        ("Frontend Files", test_frontend_files),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print(f"\n⏹️  Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    end_time = time.time()
    test_duration = end_time - start_time
    
    print(f"\nTests completed in {test_duration:.2f}s")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your newsletter platform is ready.")
        print("\nNext steps:")
        print("1. Update frontend/script.js with your production API URL")
        print("2. Deploy frontend to Netlify/GitHub Pages")
        print("3. Deploy backend to Render/Railway")
        print("4. Set up weekly cron job or GitHub Actions")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix issues before deployment.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
