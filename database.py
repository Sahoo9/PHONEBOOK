import sqlite3
from datetime import datetime
from passlib.hash import pbkdf2_sha256
import pandas as pd

class Database:
    def __init__(self):
        self.db_name = 'phonebook.db'
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP
            )
        ''')
        
        # Create contacts table with user_id foreign key
        c.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                address TEXT,
                category TEXT,
                created_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        conn.close()

    def register_user(self, username, password):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            hashed_password = pbkdf2_sha256.hash(password)
            c.execute(
                'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                (username, hashed_password, datetime.now())
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def verify_user(self, username, password):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        
        if result and pbkdf2_sha256.verify(password, result[1]):
            return result[0]  # Return user_id
        return None

    def add_contact(self, user_id, name, phone, email, address, category, notes):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO contacts (user_id, name, phone, email, address, category, created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, phone, email, address, category, datetime.now(), notes))
        conn.commit()
        conn.close()

    def get_user_contacts(self, user_id):
        conn = self.get_connection()
        contacts = pd.read_sql_query(
            "SELECT * FROM contacts WHERE user_id = ? ORDER BY name",
            conn,
            params=(user_id,)
        )
        conn.close()
        return contacts

    def search_user_contacts(self, user_id, query):
        conn = self.get_connection()
        contacts = pd.read_sql_query(
            """
            SELECT * FROM contacts 
            WHERE user_id = ? AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)
            """,
            conn,
            params=(user_id, f"%{query}%", f"%{query}%", f"%{query}%")
        )
        conn.close()
        return contacts

    def update_contact(self, user_id, contact_id, name, phone, email, address, category, notes):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            UPDATE contacts
            SET name=?, phone=?, email=?, address=?, category=?, notes=?
            WHERE id=? AND user_id=?
        ''', (name, phone, email, address, category, notes, contact_id, user_id))
        success = c.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def delete_contact(self, user_id, contact_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM contacts WHERE id=? AND user_id=?', (contact_id, user_id))
        success = c.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_contact(self, user_id, contact_id):
        conn = self.get_connection()
        contact = pd.read_sql_query(
            "SELECT * FROM contacts WHERE id=? AND user_id=?",
            conn,
            params=(contact_id, user_id)
        )
        conn.close()
        return contact.iloc[0] if not contact.empty else None