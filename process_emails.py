import json
from datetime import datetime, timedelta
from exceptions import EmailProcessingError, RuleEvaluationError
from googleapiclient.errors import HttpError

def setup_database(conn):
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS emails
                        (id TEXT PRIMARY KEY, snippet TEXT, payload TEXT, internalDate TEXT)''')
    except Exception as e:
        raise EmailProcessingError(f"Error setting up database: {e}")

def store_emails(conn, emails):
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO emails (id, snippet, payload, internalDate) VALUES (?, ?, ?, ?)",
            [(email['id'], email['snippet'], json.dumps(email['payload']), email['internalDate']) for email in emails]
        )
    except Exception as e:
        raise EmailProcessingError(f"Error storing emails: {e}")

def load_rules():
    try:
        with open('rules.json', 'r') as file:
            return json.load(file)['rules']
    except (IOError, json.JSONDecodeError) as e:
        raise RuleEvaluationError(f"Error loading rules: {e}")

def extract_email_value(field, email):
    if field in ['From', 'Subject']:
        return next((header['value'] for header in email['payload'].get('headers', []) if header['name'] == field), '')
    elif field == 'Message':
        return email['snippet']
    return ''

def evaluate_string_condition(predicate, email_value, value):
    if predicate == 'contains':
        return value in email_value
    elif predicate == 'does not contain':
        return value not in email_value
    elif predicate == 'equals':
        return value == email_value
    elif predicate == 'does not equal':
        return value != email_value
    return False

def evaluate_date_condition(predicate, email_date, value, unit):
    email_date = datetime.fromtimestamp(int(email_date) / 1000)
    current_date = datetime.now()
    delta = timedelta(days=int(value) if unit == 'days' else int(value) * 30)
    compare_date = current_date - delta

    if predicate == 'less than':
        return email_date > compare_date
    elif predicate == 'greater than':
        return email_date < compare_date
    return False

def evaluate_condition(condition, email):
    field, predicate, value = condition['field'], condition['predicate'], condition['value']
    email_value = extract_email_value(field, email)
    
    if field == 'Date received':
        return evaluate_date_condition(predicate, email['internalDate'], value, condition.get('unit', 'days'))
    return evaluate_string_condition(predicate, email_value, value)

def apply_rule(rule, email_data):
    conditions = rule['conditions']
    predicate = rule['predicate']
    try:
        if predicate == 'all':
            return all(evaluate_condition(cond, email_data) for cond in conditions)
        return any(evaluate_condition(cond, email_data) for cond in conditions)
    except Exception as e:
        raise RuleEvaluationError(f"Error applying rule: {e}")

def apply_actions(service, email_id, actions):
    for action in actions:
        if action['action'] == 'mark_as_read':
            modify_labels(service, email_id, remove_labels=['UNREAD'])
        elif action['action'] == 'mark_as_unread':
            modify_labels(service, email_id, add_labels=['UNREAD'])
        elif action['action'] == 'move_message':
            modify_labels(service, email_id, add_labels=[action['destination']])

def modify_labels(service, email_id, add_labels=None, remove_labels=None):
    body = {}
    if add_labels:
        body['addLabelIds'] = add_labels
    if remove_labels:
        body['removeLabelIds'] = remove_labels
    try:
        service.users().messages().modify(userId='me', id=email_id, body=body).execute()
    except HttpError as e:
        raise EmailProcessingError(f"Error modifying labels: {e}")

def process_emails(service, conn, rules):
    try:
        emails = conn.execute("SELECT * FROM emails").fetchall()
        for email in emails:
            email_data = {'id': email[0], 'snippet': email[1], 'payload': json.loads(email[2]), 'internalDate': email[3]}
            for rule in rules:
                if apply_rule(rule, email_data):
                    apply_actions(service, email_data['id'], rule['actions'])
    except Exception as e:
        raise EmailProcessingError(f"Error processing emails: {e}")
