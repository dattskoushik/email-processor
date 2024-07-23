import sqlite3
from typing import List, Dict
from logger import logger
from datetime import datetime

class EmailDatabase:
    def __init__(self, db_name: str = 'emails.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def create_table(self):
        self.connect()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            date TEXT,
            message TEXT,
            is_read INTEGER
        )
        ''')
        self.conn.commit()
        self.close()

    def insert_emails(self, emails: List[Dict]):
        self.connect()
        for email in emails:
            self.cursor.execute('''
            INSERT OR REPLACE INTO emails (id, sender, recipient, subject, date, message, is_read)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                email['id'],
                email.get('sender', ''),
                email.get('recipient', ''),
                email.get('subject', ''),
                email.get('date', ''),
                email.get('message', ''),
                email.get('is_read', 0)
            ))
        self.conn.commit()
        self.close()
        logger.info(f"Inserted {len(emails)} emails into the database")

    def get_all_emails(self) -> List[Dict]:
        self.connect()
        self.cursor.execute("SELECT * FROM emails")
        emails = [
            {
                'id': row[0],
                'sender': row[1],
                'recipient': row[2],
                'subject': row[3],
                'date': row[4],
                'message': row[5],
                'is_read': bool(row[6])
            }
            for row in self.cursor.fetchall()
        ]
        self.close()
        return emails

    def update_email(self, email_id: str, updates: Dict):
        self.connect()
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE emails SET {set_clause} WHERE id = ?"
        self.cursor.execute(query, list(updates.values()) + [email_id])
        self.conn.commit()
        self.close()
        logger.info(f"Updated email {email_id}")

    def delete_email(self, email_id: str):
        self.connect()
        self.cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
        self.conn.commit()
        self.close()
        logger.info(f"Deleted email {email_id}")