# ============================================================
# Dependencies:
# - typing
# ============================================================

from typing import Any, Dict, Optional

from infra_core.exceptions.base import SDKError


class PathError(SDKError):
    """
    Base exception for path module.

    :example:
        >>> raise PathError(message="generic error")
    """

    DEFAULT_CODE: str = "PATH_ERROR"


# ============================================================
# Configuration Errors
# ============================================================


class PathConfigError(PathError):
    """
    Raised when path configuration is invalid.

    :example:
        >>> raise PathConfigError(message="invalid config")
    """

    DEFAULT_CODE: str = "PATH_CONFIG_ERROR"


class InvalidPathDefinitionError(PathConfigError):
    """
    Raised when a path definition is invalid.

    :param key: str = Path key
    :param path: str = Provided path

    :example:
        >>> raise InvalidPathDefinitionError("logs", "")
    """

    DEFAULT_CODE: str = "PATH_INVALID_DEFINITION"

    def __init__(self, key: str, path: str) -> None:
        super().__init__(
            message="Invalid path definition",
            context={
                "key": key,
                "path": path,
            },
        )


class PathAlreadyExistsError(PathConfigError):
    """
    Raised when a path key already exists.

    :param key: str

    :example:
        >>> raise PathAlreadyExistsError("logs")
    """

    DEFAULT_CODE: str = "PATH_ALREADY_EXISTS"

    def __init__(self, key: str) -> None:
        super().__init__(
            message="Path already exists",
            context={"key": key},
        )


class PathNotFoundError(PathConfigError):
    """
    Raised when a path key does not exist.

    :param key: str

    :example:
        >>> raise PathNotFoundError("logs")
    """

    DEFAULT_CODE: str = "PATH_NOT_FOUND"

    def __init__(self, key: str) -> None:
        super().__init__(
            message="Path not found",
            context={"key": key},
        )


# ============================================================
# Root Errors
# ============================================================


class RootError(PathError):
    """
    Base exception for root resolution errors.

    :example:
        >>> raise RootError(message="root error")
    """

    DEFAULT_CODE: str = "PATH_ROOT_ERROR"


class RootResolutionError(RootError):
    """
    Raised when root resolution fails.

    :example:
        >>> raise RootResolutionError(message="failed")
    """

    DEFAULT_CODE: str = "PATH_ROOT_RESOLUTION_ERROR"


# ============================================================
# Resolution Errors
# ============================================================


class PathResolutionError(PathError):
    """
    Raised when path resolution fails.

    :param key: str

    :example:
        >>> raise PathResolutionError("logs")
    """

    DEFAULT_CODE: str = "PATH_RESOLUTION_ERROR"

    def __init__(
        self,
        key: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        base_context = {"key": key}
        if context:
            base_context.update(context)

        super().__init__(
            message="Failed to resolve path",
            context=base_context,
        )
