import sqlite3
from fetch_emails import authenticate_gmail, fetch_emails
from exceptions import EmailProcessingError

def main():
    try:
        service = authenticate_gmail()
        conn = sqlite3.connect('emails.db')
        emails = fetch_emails(service)
    except (EmailProcessingError) as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()