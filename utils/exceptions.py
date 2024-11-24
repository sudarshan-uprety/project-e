from typing import Optional

from utils.constant import (ERROR_BAD_REQUEST,
                            DATABASE_NOT_AVAILABLE_FOR_CONNECTION,
                            ERROR_INTERNAL_SERVER_ERROR, SERVICE_UNAVAILABLE)


class ValidationError(Exception):
    """Raised when validation error occurred."""

    def __init__(self, message=None, status_code=422, *args, **kwargs):
        self.message = message
        self.status_code = status_code
        super().__init__(self.status_code, self.message)


class DatabaseConnectionProblem(Exception):
    """Raised when connection cannot be made to the database."""

    def __init__(self):
        self.message = DATABASE_NOT_AVAILABLE_FOR_CONNECTION
        self.status_code = SERVICE_UNAVAILABLE
        super().__init__(self.status_code, self.message)


class GenericError(Exception):
    """The custom error that is raised when validation fails."""

    def __init__(self, status_code: int = ERROR_BAD_REQUEST, message: Optional[str] = None,
                 errors: Optional[dict] = None, *args, **kwargs) -> None:
        self.status_code = status_code
        self.message = message
        self.errors = errors
        super().__init__(message)


class InternalError(Exception):
    """The main error handling that handles most of the exceptions"""

    def __init__(self, status_code: int = ERROR_INTERNAL_SERVER_ERROR, message: str = None):
        self.message = f'Sorry, something went wrong in our end: {message}'
        self.status_code = status_code
        super().__init__(status_code, message)


class GenericWebsocketError(Exception):
    """The custom error that is raised when validation fails in the websocket."""

    def __init__(self, status_code: int = ERROR_BAD_REQUEST, message: str = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(status_code, message)
