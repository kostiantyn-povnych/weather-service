class BaseServiceException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return self.message


class ThirdPartyProviderUnavailable(BaseServiceException):
    """Exception raised when a third-party provider is unavailable after retries."""

    def __init__(self, provider_name: str, original_error: Exception | None = None):
        message = f"Third-party provider '{provider_name}' is currently unavailable"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message, status_code=503)


class ThirdPartyProviderError(BaseServiceException):
    """Exception raised for non-retriable third-party provider errors."""

    def __init__(self, provider_name: str, message: str, status_code: int = 502):
        full_message = f"Error from third-party provider '{provider_name}': {message}"
        super().__init__(full_message, status_code=status_code)


class InvalidProviderResponse(BaseServiceException):
    """Exception raised when provider response cannot be parsed."""

    def __init__(self, provider_name: str, parsing_error: str):
        message = f"Invalid response from provider '{provider_name}': {parsing_error}"
        super().__init__(message, status_code=502)
