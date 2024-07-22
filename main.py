from fetch_emails import fetch_emails
from process_emails import process_emails
from exceptions import EmailProcessingError
from logger import logger
from database import EmailDatabase

def main() -> None:
    try:
        emails = fetch_emails()  # This now fetches and stores emails in the database
        process_emails()  # This now processes emails from the database
    except EmailProcessingError as e:
        logger.error(f"An error occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()