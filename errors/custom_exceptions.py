from fastapi import HTTPException, status


class CustomException(Exception):
    """Base custom exception"""

    def __init__(
        self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class ValidationError(CustomException):
    """Validation error exception"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class AuthenticationError(CustomException):
    """Authentication error exception"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(CustomException):
    """Authorization error exception"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class NotFoundError(CustomException):
    """Not found error exception"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class TranscriptionError(CustomException):
    """Transcription-related error exception"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileTooLargeError(CustomException):
    """File too large error exception"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class UnsupportedMediaTypeError(CustomException):
    """Unsupported media type error exception"""

    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
