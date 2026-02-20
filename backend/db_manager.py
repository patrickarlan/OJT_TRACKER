#db_manager.py

import sqlite3
import hashlib
import os
from datetime import datetime

DB_FILE = "ojt_tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    #TABLE 1: users accounts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_hours_required REAL DEFAULT 300.0
        )
    """)
    
    #TABLE 2: stores each user's OJT progress
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracker_state (
            user_id INTEGER PRIMARY KEY,
            remaining_seconds REAL NOT NULL,
            is_clocked_in INTEGER DEFAULT 0,
            is_on_break INTEGER DEFAULT 0,
            last_closed TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    #TABLE 3: stores notes per day per user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note_date DATE NOT NULL,
            note_text TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, note_date)
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    #TABLE 4: stores attendance status per day per user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status_date DATE NOT NULL,
            status TEXT CHECK(status IN ('Present', 'Absent', 'Late')) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, status_date)
        )
    """)
    
    conn.commit()
    conn.close()
    
# PASSWORD HASHING

def hash_password(password):
    """Convert a plain password into a secure hash."""
    return hashlib.sha256(password.encode()).hexdigest()

# REGISTER AND LOGIN FUNCTIONS
def register_user(username, password, full_name="", total_hours=300):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, total_hours_required) VALUES (?, ?, ?, ?)",
            (username.strip(), hash_password(password), full_name.strip(), total_hours)
        )
        user_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO tracker_state (user_id, remaining_seconds) VALUES (?, ?)",
            (user_id, total_hours * 3600)
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        conn.close()
        
def login_user(username, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username.strip(), hash_password(password)) 
        )
        user = cursor.fetchone()
        if user:
            return True, dict(user)
        return False, None
    finally:
        conn.close()
                
# SAVE AND LOAD TRACKER STATE

def save_tracker_state(user_id, remaining_seconds, is_clocked_in, is_on_break, include_close_time=False):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        last_closed= datetime.now().strftime("%B %d, %Y at %I:%M:%S %p") if include_close_time else None
        
        if last_closed:
            cursor.execute("""
                UPDATE tracker_state
                SET remaining_seconds = ?, is_clocked_in = ?, is_on_break = ?, last_closed = ?
                WHERE user_id = ?
            """, (remaining_seconds, int(is_clocked_in), int(is_on_break), last_closed, user_id))
            conn.commit()
        else:
            cursor.execute("""
                UPDATE tracker_state
                SET remaining_seconds = ?, is_clocked_in = ?, is_on_break = ?
                WHERE user_id = ?
            """, (remaining_seconds, int(is_clocked_in), int(is_on_break), user_id))
            conn.commit()
    finally:
        conn.close()
        
def load_tracker_state(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracker_state WHERE user_id = ?", (user_id,))
        state = cursor.fetchone()
        # previous was dict(row)
        return dict(state) if state else None
    finally:
        conn.close()
        

# NOTES AND STATUS FUNTIONS

def save_note(user_id, note_date, note_text):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_notes (user_id, note_date, note_text) VALUES (?, ?, ?)
            ON CONFLICT(user_id, note_date) DO UPDATE SET note_text = excluded.note_text
        """, (user_id, note_date, note_text))
        conn.commit()
    finally:
        conn.close()
        
def delete_note(user_id, note_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_notes WHERE user_id = ? AND note_date = ?", (user_id, note_date))
        conn.commit()
    finally:
        conn.close()        
        
def load_notes(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT note_date, note_text FROM daily_notes WHERE user_id = ?", (user_id,))
        return {row["note_date"]: row["note_text"] for row in cursor.fetchall()}
    finally:
        conn.close()

def save_status(user_id, status_date, status):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_status (user_id, status_date, status) VALUES (?, ?, ?)
            ON CONFLICT(user_id, status_date) DO UPDATE SET status=excluded.status
        """, (user_id, status_date, status))
        conn.commit()
    finally:
        conn.close()
        
def delete_status(user_id, status_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_status WHERE user_id = ? AND status_date = ?", (user_id, status_date))
        conn.commit()
    finally:
        conn.close()
        
def load_daily_statuses(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT status_date, status FROM daily_status WHERE user_id = ?", (user_id,))
        return {row["status_date"]: row["status"] for row in cursor.fetchall()}
    finally:
        conn.close()