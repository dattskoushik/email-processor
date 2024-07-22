import sqlite3
from typing import List, Dict
from logger import logger

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
            subject TEXT,
            date TEXT,
            snippet TEXT
        )
        ''')
        self.conn.commit()
        self.close()

    def insert_emails(self, emails: List[Dict]):
        self.connect()
        for email in emails:
            self.cursor.execute('''
            INSERT OR REPLACE INTO emails (id, sender, subject, date, snippet)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                email['id'],
                email.get('sender', ''),
                email.get('subject', ''),
                email.get('date', ''),
                email.get('snippet', '')
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
                'subject': row[2],
                'date': row[3],
                'snippet': row[4]
            }
            for row in self.cursor.fetchall()
        ]
        self.close()
        return emails