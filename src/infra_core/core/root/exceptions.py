# ============================================================
# Dependencies:
# - typing
# ============================================================

from __future__ import annotations

from typing import Any, Dict, Optional

from infra_core.exceptions.base import SDKError


class RootError(SDKError):
    """
    Base exception for root module.

    This exception should be used as the base class for all
    root-related errors.

    :param message: str = Error description
    :param code: Optional[str] = Error code
    :param context: Optional[Dict[str, Any]] = Additional context

    :example:
        >>> from infra_core.core.root.exceptions import RootError
        >>> try:
        ...     raise RootError(message="root error")
        ... except RootError:
        ...     True
        True
    """

    DEFAULT_CODE: str = "ROOT_ERROR"


# ============================================================
# Config Errors
# ============================================================


class RootConfigError(RootError):
    """
    Base exception for root configuration errors.

    :param message: str = Error description
    :param code: Optional[str] = Error code
    :param context: Optional[Dict[str, Any]] = Additional context

    :example:
        >>> from infra_core.core.root.exceptions import RootConfigError
        >>> try:
        ...     raise RootConfigError(message="config error")
        ... except RootConfigError:
        ...     True
        True
    """

    DEFAULT_CODE: str = "ROOT_CONFIG_ERROR"


class InvalidRootMarkerError(RootConfigError):
    """
    Raised when a root marker is invalid.

    :param marker: str = Invalid marker value

    :example:
        >>> from infra_core.core.root.exceptions import InvalidRootMarkerError
        >>> try:
        ...     raise InvalidRootMarkerError("")
        ... except InvalidRootMarkerError:
        ...     True
        True
    """

    DEFAULT_CODE: str = "ROOT_INVALID_MARKER"

    def __init__(self, marker: str) -> None:
        """
        Initializes InvalidRootMarkerError.

        :param marker: str = Invalid marker

        :example:
            >>> from infra_core.core.root.exceptions import InvalidRootMarkerError
            >>> try:
            ...     raise InvalidRootMarkerError("x")
            ... except InvalidRootMarkerError:
            ...     True
            True
        """
        super().__init__(
            message="Invalid root marker",
            context={"marker": marker},
        )


class RootMarkerNotFoundError(RootConfigError):
    """
    Raised when attempting to remove a non-existent marker.

    :param marker: str = Marker value

    :example:
        >>> from infra_core.core.root.exceptions import RootMarkerNotFoundError
        >>> try:
        ...     raise RootMarkerNotFoundError(".git")
        ... except RootMarkerNotFoundError:
        ...     True
        True
    """

    DEFAULT_CODE: str = "ROOT_MARKER_NOT_FOUND"

    def __init__(self, marker: str) -> None:
        """
        Initializes RootMarkerNotFoundError.

        :param marker: str = Marker value

        :example:
            >>> from infra_core.core.root.exceptions import RootMarkerNotFoundError
            >>> try:
            ...     raise RootMarkerNotFoundError("x")
            ... except RootMarkerNotFoundError:
            ...     True
            True
        """
        super().__init__(
            message="Root marker not found",
            context={"marker": marker},
        )


# ============================================================
# Resolution Errors
# ============================================================


class RootResolutionError(RootError):
    """
    Raised when root resolution fails.

    :param message: str = Error description
    :param code: Optional[str] = Error code
    :param context: Optional[Dict[str, Any]] = Additional context

    :example:
        >>> from infra_core.core.root.exceptions import RootResolutionError
        >>> try:
        ...     raise RootResolutionError(message="resolution failed")
        ... except RootResolutionError:
        ...     True
        True
    """

    DEFAULT_CODE: str = "ROOT_RESOLUTION_ERROR"


# ============================================================
# Resolution Errors
# ============================================================


class RootNotFoundError(RootResolutionError):
    """
    Raised when no root marker is found during resolution.

    :param start_path: Optional[str] = Path where resolution started

    :example:
        >>> from infra_core.core.root.exceptions import RootNotFoundError
        >>> try:
        ...     raise RootNotFoundError("/tmp/project")
        ... except RootNotFoundError:
        ...     True
        True
    """

    DEFAULT_CODE: str = "ROOT_NOT_FOUND"

    def __init__(self, start_path: Optional[str] = None) -> None:
        """
        Initializes RootNotFoundError.

        :param start_path: Optional[str] = Initial resolution path

        :example:
            >>> from infra_core.core.root.exceptions import RootNotFoundError
            >>> try:
            ...     raise RootNotFoundError("/tmp")
            ... except RootNotFoundError:
            ...     True
            True
        """
        super().__init__(
            message="Root not found",
            context={"start_path": start_path},
        )
