# ============================================================
# Dependencies:
# - inspect
# ============================================================

from __future__ import annotations

import inspect

from infra_core.exceptions.base import SDKError


def getCurrentMethodName() -> str:
    """
    Returns current method name.

    :return: str

    :example:
        >>> isinstance(getCurrentMethodName(), str)
        True
    """
    frame = inspect.currentframe()
    if frame and frame.f_back:
        return frame.f_back.f_code.co_name
    return "unknown"


class CredentialsError(SDKError):
    """
    Base exception for all credential-related errors.

    This class extends SDKError while preserving backward compatibility.

    :example:
        >>> try:
        ...     raise CredentialsError("generic error")
        ... except CredentialsError:
        ...     True
        True
    """

    def __init__(self, message: str) -> None:
        """
        Initialize CredentialsError.

        :param message: str = Error message

        :return: None
        """
        super().__init__(message=message, code="CREDENTIALS_ERROR", context={})


class CredentialsValidationError(CredentialsError):
    """
    Raised when credential data is invalid.

    :example:
        >>> try:
        ...     raise CredentialsValidationError("invalid")
        ... except CredentialsValidationError:
        ...     True
        True
    """

    pass


class CredentialsNotFoundError(CredentialsError):
    """
    Raised when credentials cannot be found.

    :example:
        >>> try:
        ...     raise CredentialsNotFoundError("not found")
        ... except CredentialsNotFoundError:
        ...     True
        True
    """

    pass


class CredentialsDecryptionError(CredentialsError):
    """
    Raised when decryption fails.

    :example:
        >>> try:
        ...     raise CredentialsDecryptionError("decrypt error")
        ... except CredentialsDecryptionError:
        ...     True
        True
    """

    pass


class CredentialsEncryptionError(CredentialsError):
    """
    Raised when encryption fails.

    :example:
        >>> try:
        ...     raise CredentialsEncryptionError("encrypt error")
        ... except CredentialsEncryptionError:
        ...     True
        True
    """

    pass


class CredentialsSerializationError(CredentialsError):
    """
    Raised when serialization fails.

    :example:
        >>> try:
        ...     raise CredentialsSerializationError("serialization error")
        ... except CredentialsSerializationError:
        ...     True
        True
    """

    pass


class CredentialsFileError(CredentialsError):
    """
    Raised when file operations fail.

    :example:
        >>> try:
        ...     raise CredentialsFileError("file error")
        ... except CredentialsFileError:
        ...     True
        True
    """

    pass


# ============================================================
# Helper
# ============================================================


def buildExceptionMessage(class_name: str) -> str:
    """
    Build standardized exception message.

    :param class_name: str

    :return: str

    :example:
        >>> msg = buildExceptionMessage("TestClass")
        >>> "Class: TestClass" in msg
        True
    """
    return f"Class: {class_name}\n" f"Method: {getCurrentMethodName()}\n"


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    try:
        raise CredentialsValidationError(
            buildExceptionMessage("ExampleClass") + "Invalid credential format"
        )
    except CredentialsError as exc:
        print("Captured error:")
        print(exc)
