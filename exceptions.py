class EmailProcessingError(Exception):
    """Exception raised for errors in the email processing."""
    def __init__(self, message="An error occurred while processing the email."):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    """Exception raised for errors in the database operations."""
    def __init__(self, message="A database error occurred."):
        self.message = message
        super().__init__(self.message)

class RuleEvaluationError(Exception):
    """Exception raised for errors during rule evaluation."""
    def __init__(self, message="An error occurred during rule evaluation."):
        self.message = message
        super().__init__(self.message)