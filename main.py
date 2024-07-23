from fetch_emails import fetch_emails
from process_emails import process_emails
from exceptions import EmailProcessingError, DatabaseError, RuleEvaluationError
from logger import logger

def main() -> None:
    try:
        emails = fetch_emails()  # This now fetches and stores emails in the database
        process_emails(emails)  # This now processes emails from the database
    except EmailProcessingError as e:
        logger.error(f"An error occurred while processing emails: {e}")
    except DatabaseError as e:
        logger.error(f"A database error occurred: {e}")
    except RuleEvaluationError as e:
        logger.error(f"An error occurred during rule evaluation: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()