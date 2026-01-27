"""Custom exceptions for the Tuskr client."""


class TuskrAPIError(Exception):
    """Base exception for Tuskr API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TuskrAuthError(TuskrAPIError):
    """Raised when authentication fails (e.g. 401, invalid token)."""


class TuskrRateLimitError(TuskrAPIError):
    """Raised when rate limit is exceeded (429 or 10 req/s)."""
