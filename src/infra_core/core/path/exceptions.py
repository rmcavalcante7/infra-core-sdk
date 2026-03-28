# ============================================================
# Dependencies:
# - inspect
# ============================================================

import inspect


# ============================================================
# Base Exceptions
# ============================================================

class PathConfigError(Exception):
    """
    Base exception for all PathConfig-related errors.

    This exception should not be raised directly.
    Use specialized exceptions instead.

    :param message: str = Error message

    :example:
        >>> try:
        ...     raise PathConfigError("error")
        ... except PathConfigError:
        ...     True
        True
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class PathValidationError(PathConfigError):
    """
    Raised when configuration validation fails.

    :example:
        >>> try:
        ...     raise PathValidationError("invalid")
        ... except PathValidationError:
        ...     True
        True
    """
    pass


# ============================================================
# Directory Exceptions
# ============================================================

class DirectoryAlreadyExistsError(PathConfigError):
    """
    Raised when attempting to add a directory that already exists.

    :param key: str = Directory key

    :example:
        >>> try:
        ...     raise DirectoryAlreadyExistsError("logs")
        ... except DirectoryAlreadyExistsError:
        ...     True
        True
    """

    def __init__(self, key: str) -> None:
        message = (
            f"Directory '{key}' already exists."
        )
        super().__init__(message)


class DirectoryNotFoundError(PathConfigError):
    """
    Raised when attempting to access or update a non-existent directory.

    :param key: str = Directory key

    :example:
        >>> try:
        ...     raise DirectoryNotFoundError("logs")
        ... except DirectoryNotFoundError:
        ...     True
        True
    """

    def __init__(self, key: str) -> None:
        message = (
            f"Directory '{key}' not found."
        )
        super().__init__(message)


class InvalidDirectoryPathError(PathConfigError):
    """
    Raised when a directory path is invalid.

    :param key: str = Directory key
    :param path: str = Provided path

    :example:
        >>> try:
        ...     raise InvalidDirectoryPathError("logs", "")
        ... except InvalidDirectoryPathError:
        ...     True
        True
    """

    def __init__(self, key: str, path: str) -> None:
        message = (
            f"Invalid path for directory '{key}': '{path}'"
        )
        super().__init__(message)


# ============================================================
# Root Marker Exceptions
# ============================================================

class RootMarkerError(PathConfigError):
    """
    Base exception for root marker operations.
    """
    pass


class RootMarkerNotFoundError(RootMarkerError):
    """
    Raised when attempting to remove a non-existent root marker.

    :param marker: str

    :example:
        >>> try:
        ...     raise RootMarkerNotFoundError(".git")
        ... except RootMarkerNotFoundError:
        ...     True
        True
    """

    def __init__(self, marker: str) -> None:
        message = f"Root marker '{marker}' not found."
        super().__init__(message)


class InvalidRootMarkerError(RootMarkerError):
    """
    Raised when a root marker is invalid.

    :param marker: str

    :example:
        >>> try:
        ...     raise InvalidRootMarkerError("")
        ... except InvalidRootMarkerError:
        ...     True
        True
    """

    def __init__(self, marker: str) -> None:
        message = f"Invalid root marker: '{marker}'"
        super().__init__(message)


# ============================================================
# Dependency / Resolution Exceptions
# ============================================================

class PathDependencyError(PathConfigError):
    """
    Raised when dependent directory resolution fails.

    :example:
        >>> try:
        ...     raise PathDependencyError("dependency error")
        ... except PathDependencyError:
        ...     True
        True
    """
    pass


class PathResolutionError(PathConfigError):
    """
    Raised when path resolution fails.

    :example:
        >>> try:
        ...     raise PathResolutionError("error")
        ... except PathResolutionError:
        ...     True
        True
    """
    pass