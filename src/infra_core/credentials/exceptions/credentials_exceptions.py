# ============================================================
# Dependencies:
# - inspect
# ============================================================

def getCurrentMethodName() -> str:
    import inspect

    frame = inspect.currentframe()
    if frame and frame.f_back:
        return frame.f_back.f_code.co_name
    return "unknown"

class CredentialsError(Exception):
    """
    Base exception for all credential-related errors.

    This exception should be used as the root for all credential domain errors,
    enabling consistent error handling across the SDK.

    :example:
        >>> try:
        ...     raise CredentialsError("generic error")
        ... except CredentialsError:
        ...     True
        True
    """

    pass


class CredentialsValidationError(CredentialsError):
    """
    Raised when credential data is invalid or incomplete.

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
    Raised when credentials cannot be found in any configured source.

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
    Raised when decryption of credentials fails.

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
    Raised when encryption of credentials fails.

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
    Raised when serialization or deserialization fails.

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
    Raised when there are issues accessing credential-related files.

    :example:
        >>> try:
        ...     raise CredentialsFileError("file error")
        ... except CredentialsFileError:
        ...     True
        True
    """

    pass


# ============================================================
# Helper (optional, but useful for consistency)
# ============================================================


def buildExceptionMessage(class_name: str) -> str:
    """
    Build standardized exception message with class and method context.

    :param class_name: str = Name of the class raising the exception
    :return: str = Formatted base message

    :example:
        >>> msg = buildExceptionMessage("TestClass")
        >>> "Class: TestClass" in msg
        True
    """
    return (
        f"Class: {class_name}\n"
        f"Method: {getCurrentMethodName()}\n"
    )


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    try:
        raise CredentialsValidationError(
            buildExceptionMessage("ExampleClass") + "Invalid credential format"
        )
    except CredentialsError as exc:
        print("Captured error:")
        print(exc)
