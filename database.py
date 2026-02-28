import sqlite3
import os

class Database:
    def __init__(self, db_name="hospital.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def create_tables(self):
        try:
            # Users table for authentication
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            ''')

            # Pre-populate an admin user if not exists (username: admin, password: admin123)
            # Hash for 'admin123' using bcrypt
            # $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq
            import bcrypt
            self.cursor.execute("SELECT * FROM users WHERE username='admin'")
            if not self.cursor.fetchone():
                hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
                self.cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                                    ('admin', hashed.decode('utf-8'), 'admin'))

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lab_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                report TEXT NOT NULL,
                image_path TEXT
            )
            ''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                speciality TEXT NOT NULL,
                contact TEXT NOT NULL
            )
            ''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                speciality TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                contact TEXT NOT NULL
            )
            ''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ambulance_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                contact TEXT NOT NULL,
                location TEXT NOT NULL
            )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def execute_query(self, query, parameters=(), fetchone=False, fetchall=False, commit=False):
        try:
            self.cursor.execute(query, parameters)
            if commit:
                self.conn.commit()
            if fetchone:
                return self.cursor.fetchone()
            if fetchall:
                return self.cursor.fetchall()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database query error: {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()

# Create a global instance
db = Database()
