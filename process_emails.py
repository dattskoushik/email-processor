from typing import List, Dict
from logger import logger
from database import EmailDatabase
from rules_engine import RulesEngine
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from fetch_emails import mark_as_read, move_message

def process_emails(emails: List[Dict] = None) -> None:
    """Process the fetched emails."""
    db = EmailDatabase()
    if emails is None:
        emails = db.get_all_emails()
    
    rules_engine = RulesEngine('rules.json')
    
    logger.info(f"Processing {len(emails)} emails")
    
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.modify'])
    service = build('gmail', 'v1', credentials=creds)
    
    for email in emails:
        actions = rules_engine.apply_rules(email)
        for action in actions:
            if action['type'] == 'mark_as_read':
                mark_as_read(service, email['id'], action['value'])
                db.update_email(email['id'], {'is_read': action['value']})
            elif action['type'] == 'move_message':
                move_message(service, email['id'], action['value'])
                # You might want to update the database to reflect this change
        
        logger.debug(f"Processed email: Subject: {email['subject']}, From: {email['sender']}")
    
    logger.info("Email processing completed")

if __name__ == '__main__':
    process_emails()