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
