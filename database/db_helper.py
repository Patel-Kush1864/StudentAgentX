import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "student.db")

def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the SQLite database tables and seeds mock student records if the database is empty.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        deadline TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        priority TEXT DEFAULT 'Medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject_name TEXT NOT NULL,
        attended INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        generated_notes TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skills TEXT NOT NULL,
        education TEXT NOT NULL,
        projects TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    
    # Seed default user and records if users table is empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash("password123")
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?);",
            ("John Doe", "user@example.com", hashed_password)
        )
        user_id = cursor.lastrowid
        
        # Seed tasks
        tasks = [
            ("Blockchain Assignment", "Tomorrow", "Pending", "High"),
            ("Cyber Security Notes", "3 Days", "Pending", "Medium"),
            ("React Project", "7 Days", "Pending", "Low"),
            ("Math Quiz Preparation", "2 Days", "Pending", "High")
        ]
        cursor.executemany(
            "INSERT INTO tasks (user_id, task_name, deadline, status, priority) VALUES (?, ?, ?, ?, ?);",
            [(user_id, t[0], t[1], t[2], t[3]) for t in tasks]
        )
        
        # Seed attendance
        attendance_records = [
            ("Mathematics", 12, 18),
            ("Computer Science", 20, 22),
            ("Cyber Security", 10, 15),
            ("Blockchain", 7, 11)
        ]
        cursor.executemany(
            "INSERT INTO attendance (user_id, subject_name, attended, total) VALUES (?, ?, ?, ?);",
            [(user_id, a[0], a[1], a[2]) for a in attendance_records]
        )
        
        conn.commit()
        
    conn.close()
