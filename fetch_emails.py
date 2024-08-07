from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from exceptions import EmailProcessingError
from logger import logger
from typing import List, Dict
import os
import json
from database import EmailDatabase
import base64

SCOPES: List[str] = ['https://www.googleapis.com/auth/gmail.modify']

def load_credentials() -> Dict:
    """Load credentials from file or environment variables."""
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as f:
            return json.load(f)
    else:
        return {
            "web": {
                "client_id": os.environ.get('GMAIL_CLIENT_ID'),
                "project_id": os.environ.get('GMAIL_PROJECT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": os.environ.get('GMAIL_CLIENT_SECRET')
            }
        }

def authenticate_gmail() -> Credentials:
    """Authenticate with Gmail API."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_config = load_credentials()
            flow = InstalledAppFlow.from_client_config(credentials_config, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_emails() -> List[Dict]:
    """Fetch emails from Gmail and store in database."""
    try:
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        
        detailed_emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = {
                'id': msg['id'],
                'sender': next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'from'), ''),
                'recipient': next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'to'), ''),
                'subject': next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'subject'), ''),
                'date': next((header['value'] for header in msg['payload']['headers'] if header['name'].lower() == 'date'), ''),
                'message': get_email_body(msg),
                'is_read': 'UNREAD' not in msg['labelIds']
            }
            detailed_emails.append(email_data)

        # Store emails in database
        db = EmailDatabase()
        db.create_table()
        db.insert_emails(detailed_emails)

        logger.info(f"Fetched and stored {len(detailed_emails)} emails")
        return detailed_emails
    except HttpError as error:
        logger.error(f"Error fetching emails: {error}")
        raise EmailProcessingError(f"Error fetching emails: {error}")

def get_email_body(msg):
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    elif 'body' in msg['payload']:
        return base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
    return ''

def mark_as_read(service, email_id: str, read: bool = True):
    labels_to_add = []
    labels_to_remove = ['UNREAD'] if read else []
    if not read:
        labels_to_add = ['UNREAD']
    service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'addLabelIds': labels_to_add, 'removeLabelIds': labels_to_remove}
    ).execute()

def move_message(service, email_id: str, destination_label: str):
    service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'addLabelIds': [destination_label]}
    ).execute()

if __name__ == '__main__':
    emails = fetch_emails()
    print(f"Fetched {len(emails)} emails")