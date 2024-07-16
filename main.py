import sqlite3
from fetch_emails import authenticate_gmail, fetch_emails
from process_emails import setup_database, store_emails, load_rules, process_emails
from exceptions import EmailProcessingError, DatabaseError, RuleEvaluationError

def main():
    try:
        service = authenticate_gmail()
        conn = sqlite3.connect('emails.db')
        emails = fetch_emails(service)
        setup_database(conn)
        store_emails(conn, emails)
        rules = load_rules()
        process_emails(service, conn, rules)
    except (EmailProcessingError, DatabaseError, RuleEvaluationError) as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
