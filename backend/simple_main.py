"""
Simplified FastAPI backend that works with basic dependencies
"""
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Try to use FastAPI if available, otherwise provide a simple test server
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, ValidationError
    
    # Try to use EmailStr, fall back to str if email-validator not available
    try:
        from pydantic import EmailStr
        EMAIL_VALIDATION = True
    except ImportError:
        # Use a proper type alias to satisfy static type checkers
        try:
            from typing import TypeAlias  # Python 3.10+
        except ImportError:
            try:
                from typing_extensions import TypeAlias  # For older Python versions
            except ImportError:
                TypeAlias = None  # type: ignore[assignment]
        if 'TypeAlias' in globals() and TypeAlias is not None:
            EmailStr: TypeAlias = str  # Fallback to basic string
        else:
            EmailStr = str  # Runtime fallback if TypeAlias is unavailable
        EMAIL_VALIDATION = False
        print("⚠️  Email validation not available - install with: pip install pydantic[email]")
    
    FASTAPI_AVAILABLE = True
except ImportError:
    print("⚠️  FastAPI not available. Install with: pip install fastapi uvicorn")
    FASTAPI_AVAILABLE = False
    EMAIL_VALIDATION = False

# Use simple database implementation
try:
    from simple_database import SimpleNewsletterDB
    DATABASE_AVAILABLE = True
except ImportError:
    print("❌ Simple database not available")
    DATABASE_AVAILABLE = False

# Pydantic models
if FASTAPI_AVAILABLE:
    class SubscribeRequest(BaseModel):
        email: EmailStr
    
    class UnsubscribeRequest(BaseModel):
        email: EmailStr
    
    class APIResponse(BaseModel):
        success: bool
        message: str
        data: Dict[str, Any] = {}

# Initialize FastAPI app if available
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="AI Newsletter Platform API",
        description="Backend API for AI-powered newsletter platform",
        version="1.0.0"
    )

    # CORS middleware
    origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        os.getenv("FRONTEND_URL", ""),
    ]

    # Remove empty strings from origins
    origins = [origin for origin in origins if origin]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize database
    if DATABASE_AVAILABLE:
        db = SimpleNewsletterDB()
        print("✅ Database initialized")
    else:
        print("❌ Database not available")

    @app.on_event("startup")
    async def startup_event():
        print("✅ Newsletter API started successfully!")
        print(f"📧 CORS enabled for: {origins}")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy", 
            "timestamp": datetime.utcnow().isoformat(),
            "database": DATABASE_AVAILABLE,
            "fastapi": FASTAPI_AVAILABLE
        }

    # Subscribe endpoint
    @app.post("/subscribe")
    async def subscribe(request: SubscribeRequest):
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        try:
            result = db.add_subscriber(request.email)
            
            if result["success"]:
                return APIResponse(
                    success=True,
                    message=result["message"],
                    data={
                        "email": result["email"],
                        "subscribed_at": datetime.utcnow().isoformat()
                    }
                )
            else:
                return APIResponse(
                    success=False,
                    message=result["message"]
                )
        except Exception as e:
            print(f"❌ Subscribe error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your subscription."
            )

    # Unsubscribe endpoint
    @app.post("/unsubscribe")
    async def unsubscribe(request: UnsubscribeRequest):
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        try:
            result = db.unsubscribe_subscriber(request.email)
            
            if result["success"]:
                return APIResponse(
                    success=True,
                    message=result["message"],
                    data={
                        "email": result["email"],
                        "unsubscribed_at": datetime.utcnow().isoformat()
                    }
                )
            else:
                return APIResponse(
                    success=False,
                    message=result["message"]
                )
        except Exception as e:
            print(f"❌ Unsubscribe error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing your unsubscription."
            )

    # Get subscriber statistics
    @app.get("/stats")
    async def get_stats():
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=500, detail="Database not available")
        
        try:
            stats = db.get_subscriber_stats()
            logs = db.get_send_logs(limit=5)
            
            return {
                "subscriber_stats": stats,
                "recent_sends": logs,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"❌ Stats error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while fetching statistics."
            )

    # Test endpoint
    @app.get("/test")
    async def test_endpoint():
        return {
            "message": "API is working!",
            "environment": {
                "cors_origins": origins,
                "database_available": DATABASE_AVAILABLE,
                "fastapi_available": FASTAPI_AVAILABLE,
            }
        }

    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Endpoint not found"}
        )

    @app.exception_handler(422)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid input data. Please check your request and try again.",
                "errors": exc.errors() if hasattr(exc, 'errors') else []
            }
        )

    if __name__ == "__main__":
        try:
            import uvicorn
            
            port = int(os.getenv("PORT", 8000))
            host = os.getenv("HOST", "0.0.0.0")
            
            print(f"🚀 Starting server on {host}:{port}")
            uvicorn.run(
                "simple_main:app",
                host=host,
                port=port,
                reload=True if os.getenv("DEBUG", "False").lower() == "true" else False
            )
        except ImportError:
            print("❌ uvicorn not available. Install with: pip install uvicorn")
            sys.exit(1)

else:
    # Fallback for when FastAPI is not available
    def simple_server():
        """Simple HTTP server for testing without FastAPI"""
        import http.server
        import socketserver
        import json
        from urllib.parse import urlparse, parse_qs
        
        class NewsletterHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {
                        "status": "healthy",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Simple server running (FastAPI not available)"
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path in ["/subscribe", "/unsubscribe"]:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    
                    try:
                        data = json.loads(post_data.decode('utf-8'))
                        email = data.get('email')
                        
                        if not email:
                            self.send_error(400, "Email required")
                            return
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        response = {
                            "success": True,
                            "message": f"{'Subscribed' if self.path == '/subscribe' else 'Unsubscribed'} successfully (demo mode)",
                            "email": email
                        }
                        self.wfile.write(json.dumps(response).encode())
                    
                    except Exception as e:
                        self.send_error(500, str(e))
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_OPTIONS(self):
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
        
        port = 8000
        with socketserver.TCPServer(("", port), NewsletterHandler) as httpd:
            print(f"🚀 Simple server running on http://localhost:{port}")
            print("📧 Endpoints: /health, /subscribe, /unsubscribe")
            print("⚠️  This is a demo server. Install FastAPI for full functionality.")
            httpd.serve_forever()

    if __name__ == "__main__":
        simple_server()

# Test function
def test_api():
    """Test the API functionality"""
    print("🧪 Testing Newsletter API...")
    
    if not FASTAPI_AVAILABLE:
        print("⚠️  FastAPI not available - testing simple database only")
        if DATABASE_AVAILABLE:
            from simple_database import test_database
            test_database()
        return
    
    # Test with FastAPI TestClient if available
    try:
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test subscribe
        response = client.post("/subscribe", json={"email": "test@example.com"})
        print(f"Subscribe: {response.status_code} - {response.json()}")
        
        # Test stats
        response = client.get("/stats")
        print(f"Stats: {response.status_code}")
        
        # Test unsubscribe
        response = client.post("/unsubscribe", json={"email": "test@example.com"})
        print(f"Unsubscribe: {response.status_code} - {response.json()}")
        
        print("✅ API test completed!")
        
    except ImportError:
        print("⚠️  TestClient not available")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_api()
    else:
        # Start the appropriate server
        pass
