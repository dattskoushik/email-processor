class EmailProcessingError(Exception):
    """Exception raised for errors in the email processing."""
    def __init__(self, message="An error occurred while processing the email."):
        self.message = message
        super().__init__(self.message)
