import json
from typing import Dict, List
from datetime import datetime, timedelta

class RulesEngine:
    def __init__(self, rules_file: str):
        with open(rules_file, 'r') as f:
            self.rules = json.load(f)

    def apply_rules(self, email: Dict) -> List[Dict]:
        actions = []
        for rule in self.rules:
            if self.check_conditions(rule['conditions'], email, rule['predicate']):
                actions.extend(rule['actions'])
        return actions

    def check_conditions(self, conditions: List[Dict], email: Dict, predicate: str) -> bool:
        results = []
        for condition in conditions:
            result = self.check_condition(condition, email)
            results.append(result)
        
        if predicate == 'all':
            return all(results)
        elif predicate == 'any':
            return any(results)
        else:
            raise ValueError(f"Invalid predicate: {predicate}")

    def check_condition(self, condition: Dict, email: Dict) -> bool:
        field = condition['field']
        predicate = condition['predicate']
        value = condition['value']

        if field not in email:
            return False

        if field == 'date':
            email_date = datetime.strptime(email[field], "%a, %d %b %Y %H:%M:%S %z")
            if predicate == 'less_than':
                days = int(value.split()[0])
                return email_date > datetime.now(email_date.tzinfo) - timedelta(days=days)
            elif predicate == 'greater_than':
                days = int(value.split()[0])
                return email_date < datetime.now(email_date.tzinfo) - timedelta(days=days)
        else:
            if predicate == 'contains':
                return value.lower() in email[field].lower()
            elif predicate == 'not_contains':
                return value.lower() not in email[field].lower()
            elif predicate == 'equals':
                return value.lower() == email[field].lower()
            elif predicate == 'not_equals':
                return value.lower() != email[field].lower()

        return False