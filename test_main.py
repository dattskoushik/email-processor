import unittest
from unittest.mock import patch, MagicMock
from database import EmailDatabase
from rules_engine import RulesEngine
from process_emails import process_emails
from fetch_emails import fetch_emails
from exceptions import EmailProcessingError, DatabaseError, RuleEvaluationError

class TestEmailProcessor(unittest.TestCase):

    @patch('database.EmailDatabase')
    def setUp(self, mock_db):
        self.mock_db = mock_db
        self.db_instance = self.mock_db.return_value
        self.db_instance.get_all_emails.return_value = [
            {
                'id': '1',
                'sender': 'test@tenmiles.com',
                'recipient': 'recipient@example.com',
                'subject': 'Interview Schedule',
                'date': 'Tue, 23 Jul 2024 10:00:00 +0000',
                'message': 'Test message content',
                'is_read': False
            }
        ]

    @patch('rules_engine.RulesEngine')
    def test_process_emails(self, mock_rules_engine):
        mock_rules_instance = mock_rules_engine.return_value
        mock_rules_instance.apply_rules.return_value = [
            {'type': 'mark_as_read', 'value': True},
            {'type': 'move_message', 'value': 'INBOX'}
        ]

        with patch('process_emails.mark_as_read') as mock_mark_read, \
             patch('process_emails.move_message') as mock_move_message:
            
            process_emails()

            self.db_instance.get_all_emails.assert_called_once()
            mock_rules_instance.apply_rules.assert_called_once()
            mock_mark_read.assert_called_once()
            mock_move_message.assert_called_once()

    @patch('fetch_emails.authenticate_gmail')
    @patch('fetch_emails.build')
    def test_fetch_emails(self, mock_build, mock_auth):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': '1'}]
        }
        mock_service.users().messages().get().execute.return_value = {
            'id': '1',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'To', 'value': 'recipient@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Tue, 23 Jul 2024 10:00:00 +0000'}
                ]
            },
            'snippet': 'Test snippet',
            'labelIds': []
        }

        emails = fetch_emails()

        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['sender'], 'sender@example.com')
        self.assertEqual(emails[0]['subject'], 'Test Subject')

    def test_database_operations(self):
        test_email = {
            'id': '1',
            'sender': 'test@example.com',
            'recipient': 'recipient@example.com',
            'subject': 'Test Subject',
            'date': 'Tue, 23 Jul 2024 10:00:00 +0000',
            'message': 'Test message',
            'is_read': False
        }
        self.db_instance.insert_emails.return_value = None
        self.db_instance.get_all_emails.return_value = [test_email]
        self.db_instance.update_email.return_value = None

        # Test insert
        self.db_instance.insert_emails([test_email])
        self.db_instance.insert_emails.assert_called_once()

        # Test get all
        emails = self.db_instance.get_all_emails()
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['sender'], 'test@example.com')

        # Test update
        self.db_instance.update_email('1', {'is_read': True})
        self.db_instance.update_email.assert_called_once_with('1', {'is_read': True})

    def test_rule_engine(self):
        rules_engine = RulesEngine('rules.json')
        test_email = {
            'id': '1',
            'sender': 'test@tenmiles.com',
            'subject': 'Interview Schedule',
            'date': 'Tue, 23 Jul 2024 10:00:00 +0000',
            'message': 'Test message',
            'is_read': False
        }

        actions = rules_engine.apply_rules(test_email)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]['type'], 'move_message')
        self.assertEqual(actions[1]['type'], 'mark_as_read')

    def test_exceptions(self):
        with self.assertRaises(EmailProcessingError):
            raise EmailProcessingError("Test error")
        
        with self.assertRaises(DatabaseError):
            raise DatabaseError("Test database error")
        
        with self.assertRaises(RuleEvaluationError):
            raise RuleEvaluationError("Test rule evaluation error")

if __name__ == '__main__':
    unittest.main()