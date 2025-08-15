"""
Standalone database module for testing without dependencies
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

# Simple database implementation using sqlite3 directly
class SimpleNewsletterDB:
    def __init__(self, db_path: str = "newsletter.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create subscribers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create send_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS send_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_count INTEGER DEFAULT 0,
                failures INTEGER DEFAULT 0,
                latency_ms INTEGER DEFAULT 0,
                error_details TEXT,
                newsletter_subject TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def add_subscriber(self, email: str) -> Dict[str, Any]:
        """Add a new subscriber"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if subscriber already exists
            cursor.execute("SELECT email, status FROM subscribers WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                if existing[1] == "unsubscribed":
                    # Reactivate unsubscribed user
                    cursor.execute(
                        "UPDATE subscribers SET status = 'active', updated_at = ? WHERE email = ?",
                        (datetime.now().isoformat(), email)
                    )
                    conn.commit()
                    return {"success": True, "message": "Reactivated subscription", "email": email}
                else:
                    return {"success": False, "message": "Email already subscribed", "email": email}
            
            # Add new subscriber
            cursor.execute(
                "INSERT INTO subscribers (email, status) VALUES (?, 'active')",
                (email,)
            )
            conn.commit()
            return {"success": True, "message": "Successfully subscribed", "email": email}
            
        except sqlite3.IntegrityError:
            return {"success": False, "message": "Email already exists", "email": email}
        except Exception as e:
            return {"success": False, "message": f"Database error: {str(e)}", "email": email}
        finally:
            conn.close()
    
    def unsubscribe_subscriber(self, email: str) -> Dict[str, Any]:
        """Unsubscribe a subscriber"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if subscriber exists
            cursor.execute("SELECT email, status FROM subscribers WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if not existing:
                return {"success": False, "message": "Email not found in subscriber list", "email": email}
            
            if existing[1] == "unsubscribed":
                return {"success": False, "message": "Email already unsubscribed", "email": email}
            
            # Unsubscribe
            cursor.execute(
                "UPDATE subscribers SET status = 'unsubscribed', updated_at = ? WHERE email = ?",
                (datetime.now().isoformat(), email)
            )
            conn.commit()
            return {"success": True, "message": "Successfully unsubscribed", "email": email}
            
        except Exception as e:
            return {"success": False, "message": f"Database error: {str(e)}", "email": email}
        finally:
            conn.close()
    
    def get_active_subscribers(self) -> List[str]:
        """Get all active subscriber emails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT email FROM subscribers WHERE status = 'active'")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_subscriber_stats(self) -> Dict[str, int]:
        """Get subscriber statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM subscribers WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subscribers")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subscribers WHERE status = 'unsubscribed'")
            unsubscribed_count = cursor.fetchone()[0]
            
            return {
                "active": active_count,
                "total": total_count,
                "unsubscribed": unsubscribed_count
            }
        finally:
            conn.close()
    
    def log_newsletter_send(self, sent_count: int, failures: int, latency_ms: int, 
                           error_details: Optional[str] = None, newsletter_subject: Optional[str] = None):
        """Log newsletter sending statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO send_logs 
                (sent_count, failures, latency_ms, error_details, newsletter_subject)
                VALUES (?, ?, ?, ?, ?)
            ''', (sent_count, failures, latency_ms, error_details, newsletter_subject))
            conn.commit()
        finally:
            conn.close()
    
    def get_send_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent send logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT date, sent_count, failures, latency_ms, error_details, newsletter_subject
                FROM send_logs 
                ORDER BY date DESC 
                LIMIT ?
            ''', (limit,))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "date": row[0],
                    "sent_count": row[1],
                    "failures": row[2],
                    "latency_ms": row[3],
                    "error_details": row[4],
                    "newsletter_subject": row[5]
                })
            return logs
        finally:
            conn.close()

def test_database():
    """Test the database functionality"""
    print("🧪 Testing Simple Newsletter Database...")
    
    # Initialize database
    db = SimpleNewsletterDB("test_newsletter.db")
    
    # Test adding subscriber
    result = db.add_subscriber("test@example.com")
    print(f"Add subscriber: {result}")
    
    # Test duplicate subscriber
    result = db.add_subscriber("test@example.com")
    print(f"Duplicate subscriber: {result}")
    
    # Test getting active subscribers
    subscribers = db.get_active_subscribers()
    print(f"Active subscribers: {subscribers}")
    
    # Test getting stats
    stats = db.get_subscriber_stats()
    print(f"Subscriber stats: {stats}")
    
    # Test unsubscribe
    result = db.unsubscribe_subscriber("test@example.com")
    print(f"Unsubscribe: {result}")
    
    # Test stats after unsubscribe
    stats = db.get_subscriber_stats()
    print(f"Stats after unsubscribe: {stats}")
    
    # Test logging
    db.log_newsletter_send(5, 1, 1500, "Some email failed", "Weekly Update #1")
    
    # Test getting logs
    logs = db.get_send_logs()
    print(f"Send logs: {logs}")
    
    # Clean up test database
    os.remove("test_newsletter.db")
    print("✅ Database test completed!")

if __name__ == "__main__":
    test_database()
