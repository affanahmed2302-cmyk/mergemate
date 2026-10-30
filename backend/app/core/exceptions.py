from typing import Any

class MergeMateError(Exception):
    def __init__(self, message: str, *, code: str = "internal_error", status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

class ValidationError(MergeMateError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="validation_error", status_code=400, details=details)

class NotFoundError(MergeMateError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="not_found", status_code=404)

class GitHubError(MergeMateError):
    def __init__(self, message: str, *, status_code: int = 502, details: Any = None):
        super().__init__(message, code="github_error", status_code=status_code, details=details)
