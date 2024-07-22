from typing import List, Dict
from logger import logger
from database import EmailDatabase

def process_emails(emails: List[Dict] = None) -> None:
    """Process the fetched emails."""
    db = EmailDatabase()
    if emails is None:
        emails = db.get_all_emails()
    
    logger.info(f"Processing {len(emails)} emails")
    for email in emails:
        # Add your email processing logic here
        logger.debug(f"Processing email: Subject: {email['subject']}, From: {email['sender']}")
    logger.info("Email processing completed")

if __name__ == '__main__':
    process_emails()