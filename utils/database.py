import sqlite3
import json
from datetime import datetime
from pathlib import Path
import hashlib

DB_PATH = Path(__file__).parent.parent / "databot.db"

def init_database():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table for profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT,
            api_key_encrypted TEXT,
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conv_id TEXT PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            dataset_name TEXT,
            messages TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Query logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            conv_id TEXT,
            query TEXT,
            response TEXT,
            has_chart BOOLEAN,
            execution_time_ms FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (conv_id) REFERENCES conversations(conv_id)
        )
    """)
    
    # User authentication table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_auth (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Saved queries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_queries (
            query_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT,
            query_text TEXT,
            dataset_name TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Query patterns table for analytics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_patterns (
            pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            query_keyword TEXT,
            frequency INTEGER DEFAULT 1,
            last_used TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()

def get_or_create_user(user_id: str, email: str = None) -> dict:
    """Get or create a user profile."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, email) VALUES (?, ?)",
            (user_id, email)
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
    
    conn.close()
    return {
        "user_id": user[0],
        "email": user[1],
        "api_key_encrypted": user[2],
        "preferences": json.loads(user[3]) if user[3] else {},
        "created_at": user[4]
    }

def save_conversation(user_id: str, conv_id: str, title: str, dataset_name: str, messages: list):
    """Save a conversation to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO conversations 
        (conv_id, user_id, title, dataset_name, messages, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (conv_id, user_id, title, dataset_name, json.dumps(messages)))
    
    conn.commit()
    conn.close()

def get_conversations(user_id: str) -> list:
    """Get all conversations for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT conv_id, title, dataset_name, created_at, updated_at 
        FROM conversations 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
    """, (user_id,))
    
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            "conv_id": row[0],
            "title": row[1],
            "dataset_name": row[2],
            "created_at": row[3],
            "updated_at": row[4]
        })
    
    conn.close()
    return conversations

def load_conversation(conv_id: str) -> dict:
    """Load a specific conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT conv_id, title, dataset_name, messages, created_at 
        FROM conversations 
        WHERE conv_id = ?
    """, (conv_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "conv_id": result[0],
            "title": result[1],
            "dataset_name": result[2],
            "messages": json.loads(result[3]),
            "created_at": result[4]
        }
    return None

def log_query(user_id: str, conv_id: str, query: str, response: str, has_chart: bool, execution_time_ms: float):
    """Log a query and response."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO query_logs 
        (user_id, conv_id, query, response, has_chart, execution_time_ms)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, conv_id, query, response, has_chart, execution_time_ms))
    
    conn.commit()
    conn.close()

def get_query_history(user_id: str, limit: int = 50) -> list:
    """Get recent query history for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT query, response, has_chart, timestamp 
        FROM query_logs 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (user_id, limit))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            "query": row[0],
            "response": row[1],
            "has_chart": row[2],
            "timestamp": row[3]
        })
    
    conn.close()
    return history

def save_user_preferences(user_id: str, preferences: dict):
    """Save user preferences."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE users SET preferences = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
        (json.dumps(preferences), user_id)
    )
    
    conn.commit()
    conn.close()

def get_user_preferences(user_id: str) -> dict:
    """Get user preferences."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT preferences FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        return json.loads(result[0])
    return {}

def get_conversation_stats(user_id: str) -> dict:
    """Get conversation and query statistics for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE user_id = ?", (user_id,))
    total_conversations = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM query_logs WHERE user_id = ?", (user_id,))
    total_queries = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM query_logs WHERE user_id = ? AND has_chart = 1", (user_id,))
    charts_generated = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(execution_time_ms) FROM query_logs WHERE user_id = ?", (user_id,))
    avg_execution_time = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_conversations": total_conversations,
        "total_queries": total_queries,
        "charts_generated": charts_generated,
        "avg_execution_time_ms": round(avg_execution_time, 2)
    }

# ============= AUTHENTICATION FUNCTIONS =============

def create_user_account(user_id: str, username: str, password_hash: str, email: str = None) -> bool:
    """Create a new user account with authentication."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create user profile
        cursor.execute(
            "INSERT INTO users (user_id, email) VALUES (?, ?)",
            (user_id, email)
        )
        
        # Create authentication record
        cursor.execute(
            "INSERT INTO user_auth (user_id, username, password_hash) VALUES (?, ?, ?)",
            (user_id, username, password_hash)
        )
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username: str) -> dict:
    """Get user by username for login."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ua.user_id, ua.password_hash, u.email 
        FROM user_auth ua
        JOIN users u ON ua.user_id = u.user_id
        WHERE ua.username = ?
    """, (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "user_id": result[0],
            "password_hash": result[1],
            "email": result[2]
        }
    return None

def update_last_login(user_id: str):
    """Update last login timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_auth SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

# ============= SAVED QUERIES FUNCTIONS =============

def save_query_template(user_id: str, title: str, query_text: str, dataset_name: str, tags: str = "") -> bool:
    """Save a query template for future use."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO saved_queries (user_id, title, query_text, dataset_name, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, query_text, dataset_name, tags))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_saved_queries(user_id: str) -> list:
    """Get all saved queries for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT query_id, title, query_text, dataset_name, tags, usage_count, created_at
        FROM saved_queries
        WHERE user_id = ?
        ORDER BY usage_count DESC, created_at DESC
    """, (user_id,))
    
    queries = []
    for row in cursor.fetchall():
        queries.append({
            "query_id": row[0],
            "title": row[1],
            "query_text": row[2],
            "dataset_name": row[3],
            "tags": row[4],
            "usage_count": row[5],
            "created_at": row[6]
        })
    
    conn.close()
    return queries

def use_saved_query(query_id: int):
    """Increment usage count for a saved query."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE saved_queries SET usage_count = usage_count + 1 WHERE query_id = ?",
        (query_id,)
    )
    conn.commit()
    conn.close()

def delete_saved_query(query_id: int):
    """Delete a saved query."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_queries WHERE query_id = ?", (query_id,))
    conn.commit()
    conn.close()

# ============= ANALYTICS FUNCTIONS =============

def get_query_patterns(user_id: str, limit: int = 10) -> list:
    """Get most frequently asked query patterns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT query_keyword, frequency, last_used
        FROM query_patterns
        WHERE user_id = ?
        ORDER BY frequency DESC
        LIMIT ?
    """, (user_id, limit))
    
    patterns = []
    for row in cursor.fetchall():
        patterns.append({
            "keyword": row[0],
            "frequency": row[1],
            "last_used": row[2]
        })
    
    conn.close()
    return patterns

def track_query_pattern(user_id: str, query_text: str):
    """Track query patterns for analytics."""
    # Extract keywords (first few words)
    keywords = " ".join(query_text.split()[:3]).lower()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT pattern_id FROM query_patterns WHERE user_id = ? AND query_keyword = ?",
        (user_id, keywords)
    )
    
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("""
            UPDATE query_patterns 
            SET frequency = frequency + 1, last_used = CURRENT_TIMESTAMP
            WHERE user_id = ? AND query_keyword = ?
        """, (user_id, keywords))
    else:
        cursor.execute("""
            INSERT INTO query_patterns (user_id, query_keyword, last_used)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, keywords))
    
    conn.commit()
    conn.close()

def get_dataset_usage(user_id: str) -> dict:
    """Get usage statistics by dataset."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT dataset_name, COUNT(*) as count
        FROM conversations
        WHERE user_id = ?
        GROUP BY dataset_name
        ORDER BY count DESC
    """, (user_id,))
    
    datasets = {}
    for row in cursor.fetchall():
        datasets[row[0]] = row[1]
    
    conn.close()
    return datasets

def get_query_analytics(user_id: str) -> dict:
    """Get comprehensive query analytics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total queries by date (last 30 days)
    cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM query_logs
        WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """, (user_id,))
    
    daily_queries = {}
    for row in cursor.fetchall():
        daily_queries[row[0]] = row[1]
    
    conn.close()
    
    return {
        "daily_queries": daily_queries,
        "response_times": get_response_time_stats(user_id),
        "chart_usage": get_chart_usage_stats(user_id)
    }

def get_response_time_stats(user_id: str) -> dict:
    """Get response time statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            MIN(execution_time_ms) as min_time,
            MAX(execution_time_ms) as max_time,
            AVG(execution_time_ms) as avg_time
        FROM query_logs
        WHERE user_id = ?
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        "min_ms": round(result[0], 2) if result[0] else 0,
        "max_ms": round(result[1], 2) if result[1] else 0,
        "avg_ms": round(result[2], 2) if result[2] else 0
    }

def get_chart_usage_stats(user_id: str) -> dict:
    """Get chart generation statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN has_chart = 1 THEN 1 ELSE 0 END) as with_charts
        FROM query_logs
        WHERE user_id = ?
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    total = result[0] or 1
    with_charts = result[1] or 0
    
    return {
        "total_queries": total,
        "with_charts": with_charts,
        "chart_percentage": round((with_charts / total * 100), 1) if total > 0 else 0
    }
