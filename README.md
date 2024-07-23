# Gmail Rule-Based Email Processor

This Python application integrates with the Gmail API to fetch emails and process them based on user-defined rules.

## Requirements

- Python 3.12
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 Client ID credentials

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/gmail-rule-processor.git
   cd gmail-rule-processor
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up Google Cloud Project and OAuth 2.0 credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API for your project
   - Create OAuth 2.0 Client ID credentials
   - Download the credentials JSON file

5. Create your `credentials.json` file:
   - Copy the `credentials.sample.json` file to `credentials.json`
   - Open `credentials.json` and replace the placeholder values with your actual OAuth 2.0 credentials

   ```
   cp credentials.sample.json credentials.json
   ```

   Note: `credentials.json` is listed in `.gitignore` to prevent accidental commit of sensitive data.

## Configuration

1. Edit the `rules.json` file to define your email processing rules.

## Running the Application

1. Run the main script:
   ```
   python main.py
   ```

2. The first time you run the script, it will open a browser window for you to authenticate with your Google account. Grant the necessary permissions.

3. The application will fetch emails from your inbox, store them in a local SQLite database, and process them according to the rules defined in `rules.json`.

## Running Tests

To run the unit tests:

```
python -m unittest test_main.py
```

## Security Note

Never commit your actual `credentials.json` file to the repository. The `credentials.sample.json` file is provided as a template, but your real credentials should be kept private.
