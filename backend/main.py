from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import os
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Import our modules
from database import SubscriberDB, init_db
from models import SubscribeRequest, UnsubscribeRequest, APIResponse

# Load environment variables
load_dotenv()

# Database session dependency
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./newsletter.db")
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize FastAPI app
app = FastAPI(
    title="DataDispatch API",
    description="Backend API for DataDispatch AI-powered newsletter platform",
    version="1.0.0",
)

# CORS middleware
DEV_MODE = os.getenv("DEBUG", "False").lower() == "true"
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    os.getenv("FRONTEND_URL", ""),
    "null",  # allow file:// origins in browsers (Origin: null)
]

# Remove empty strings from origins
origins = [origin for origin in origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=".*" if DEV_MODE else None,  # in dev, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ DataDispatch API started successfully!")
    print(f"📧 CORS enabled for: {origins}")
    if DEV_MODE:
        print("🔓 DEV_MODE CORS regex enabled: allow all origins")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Subscribe endpoint
@app.post("/subscribe", response_model=APIResponse)
async def subscribe(request: SubscribeRequest, db: Session = Depends(get_db)):
    try:
        subscriber_db = SubscriberDB(db)
        subscriber = subscriber_db.create_subscriber(request.email)

        return APIResponse(
            success=True,
            message="Successfully subscribed to newsletter!",
            data={
                "email": subscriber.email,
                "status": subscriber.status,
                "subscribed_at": subscriber.created_at.isoformat(),
            },
        )
    except ValueError as e:
        error_message = str(e)
        if "already subscribed" in error_message:
            return APIResponse(
                success=False,
                message="This email is already subscribed to our newsletter.",
            )
        else:
            return APIResponse(success=False, message=error_message)
    except Exception as e:
        print(f"❌ Subscribe error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your subscription. Please try again later.",
        )


# Unsubscribe endpoint
@app.post("/unsubscribe", response_model=APIResponse)
async def unsubscribe(request: UnsubscribeRequest, db: Session = Depends(get_db)):
    try:
        subscriber_db = SubscriberDB(db)
        subscriber_db.unsubscribe_subscriber(request.email)

        return APIResponse(
            success=True,
            message="Successfully unsubscribed from newsletter. We're sorry to see you go!",
            data={
                "email": request.email,
                "unsubscribed_at": datetime.utcnow().isoformat(),
            },
        )
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message:
            return APIResponse(
                success=False,
                message="This email address is not in our subscriber list.",
            )
        elif "already unsubscribed" in error_message:
            return APIResponse(
                success=False,
                message="This email is already unsubscribed from our newsletter.",
            )
        else:
            return APIResponse(success=False, message=error_message)
    except Exception as e:
        print(f"❌ Unsubscribe error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your unsubscription. Please try again later.",
        )


# Get subscriber statistics (admin endpoint)
@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    try:
        subscriber_db = SubscriberDB(db)
        stats = subscriber_db.get_subscriber_count()

        return {"subscriber_stats": stats, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        print(f"❌ Stats error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching statistics."
        )


# Test endpoint for development
@app.get("/test")
async def test_endpoint():
    return {
        "message": "API is working!",
        "environment": {
            "cors_origins": origins,
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./newsletter.db"),
        },
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})


@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid input data. Please check your request and try again.",
            "errors": exc.errors() if hasattr(exc, "errors") else [],
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("DEBUG", "False").lower() == "true" else False,
    )
