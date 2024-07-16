import unittest
from fetch_emails import authenticate_gmail, fetch_emails
from process_emails import setup_database, store_emails, load_rules, process_emails
import sqlite3

class TestEmailProcessor(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        setup_database(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_database_setup(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails';")
        table = cursor.fetchone()
        self.assertIsNotNone(table)
    
    def test_store_emails(self):
        emails = [
            {
                'id': '1', 'snippet': 'test snippet', 'payload': '{}', 'internalDate': '1234567890'
            }
        ]
        store_emails(self.conn, emails)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM emails;")
        stored_emails = cursor.fetchall()
        self.assertEqual(len(stored_emails), 1)
    
    def test_load_rules(self):
        rules = load_rules()
        self.assertTrue(len(rules) > 0)

if __name__ == '__main__':
    unittest.main()
