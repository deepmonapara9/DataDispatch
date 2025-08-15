import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Integer, String, DateTime, Text
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session,
    Mapped,
    mapped_column,
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./newsletter.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class Subscriber(Base):
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="active"
    )  # active, unsubscribed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SendLog(Base):
    __tablename__ = "send_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failures: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    newsletter_subject: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database operations
class SubscriberDB:
    def __init__(self, db: Session):
        self.db = db

    def create_subscriber(self, email: str) -> Subscriber:
        """Create a new subscriber"""
        # Check if already exists
        existing = self.get_subscriber_by_email(email)
        if existing:
            if existing.status == "unsubscribed":
                # Reactivate unsubscribed user
                existing.status = "active"
                existing.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing)
                return existing
            else:
                raise ValueError("Email already subscribed")

        subscriber = Subscriber(email=email, status="active")
        self.db.add(subscriber)
        self.db.commit()
        self.db.refresh(subscriber)
        return subscriber

    def get_subscriber_by_email(self, email: str) -> Optional[Subscriber]:
        """Get subscriber by email"""
        return self.db.query(Subscriber).filter(Subscriber.email == email).first()

    def unsubscribe_subscriber(self, email: str) -> bool:
        """Unsubscribe a subscriber"""
        subscriber = self.get_subscriber_by_email(email)
        if not subscriber:
            raise ValueError("Email not found in subscriber list")

        if subscriber.status == "unsubscribed":
            raise ValueError("Email already unsubscribed")

        subscriber.status = "unsubscribed"
        subscriber.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_active_subscribers(self) -> List[Subscriber]:
        """Get all active subscribers"""
        return self.db.query(Subscriber).filter(Subscriber.status == "active").all()

    def get_subscriber_count(self) -> dict:
        """Get subscriber statistics"""
        active_count = (
            self.db.query(Subscriber).filter(Subscriber.status == "active").count()
        )
        total_count = self.db.query(Subscriber).count()
        unsubscribed_count = (
            self.db.query(Subscriber)
            .filter(Subscriber.status == "unsubscribed")
            .count()
        )

        return {
            "active": active_count,
            "total": total_count,
            "unsubscribed": unsubscribed_count,
        }


class SendLogDB:
    def __init__(self, db: Session):
        self.db = db

    def create_send_log(
        self,
        sent_count: int,
        failures: int,
        latency_ms: int,
        error_details: Optional[str] = None,
        newsletter_subject: Optional[str] = None,
    ) -> SendLog:
        """Create a new send log entry"""
        log = SendLog(
            sent_count=sent_count,
            failures=failures,
            latency_ms=latency_ms,
            error_details=error_details,
            newsletter_subject=newsletter_subject,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_recent_logs(self, limit: int = 10) -> List[SendLog]:
        """Get recent send logs"""
        return self.db.query(SendLog).order_by(SendLog.date.desc()).limit(limit).all()

    def get_send_statistics(self) -> dict:
        """Get sending statistics"""
        logs = self.db.query(SendLog).all()

        if not logs:
            return {
                "total_sent": 0,
                "total_failures": 0,
                "average_latency": 0,
                "success_rate": 0,
            }

        total_sent = sum(log.sent_count for log in logs)
        total_failures = sum(log.failures for log in logs)
        average_latency = sum(log.latency_ms for log in logs) / len(logs)
        success_rate = (
            (total_sent / (total_sent + total_failures)) * 100
            if (total_sent + total_failures) > 0
            else 0
        )

        return {
            "total_sent": total_sent,
            "total_failures": total_failures,
            "average_latency": round(average_latency, 2),
            "success_rate": round(success_rate, 2),
        }


# Initialize database
def init_db():
    """Initialize database with tables"""
    create_tables()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
