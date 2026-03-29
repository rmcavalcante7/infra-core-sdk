# ============================================================
# Dependencies:
# - dataclasses
# - typing
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from infra_core.core.root.exceptions import (
    InvalidRootMarkerError,
    RootMarkerNotFoundError,
)


@dataclass(frozen=True)
class RootConfig:
    """
    Immutable configuration for root resolution.

    Defines which markers are used to identify the project root.

    :param markers: Tuple[str, ...] = Root detection markers

    :example:
        >>> from infra_core.core.root.root_config import RootConfig
        >>> config = RootConfig()
        >>> isinstance(config.markers, tuple)
        True
    """

    markers: Tuple[str, ...] = field(default_factory=tuple)

    # ============================================================
    # Initialization
    # ============================================================

    def __post_init__(self) -> None:
        """
        Initializes default markers and validates configuration.

        :return: None

        :raises InvalidRootMarkerError:
            When markers are invalid

        :example:
            >>> from infra_core.core.root.root_config import RootConfig
            >>> config = RootConfig()
            >>> isinstance(config.markers, tuple)
            True
        """
        if not self.markers:
            object.__setattr__(self, "markers", self._defaultMarkers())
        else:
            self._validateMarkers(self.markers)

    # ============================================================
    # Public Methods
    # ============================================================

    def addMarker(self, marker: str) -> "RootConfig":
        """
        Adds a new root marker.

        :param marker: str = Marker value

        :return: RootConfig = New configuration instance

        :raises InvalidRootMarkerError:
            When marker is invalid

        :example:
            >>> from infra_core.core.root.root_config import RootConfig
            >>> config = RootConfig()
            >>> config = config.addMarker(".env")
            >>> ".env" in config.markers
            True
        """
        self._validateMarker(marker)

        if marker in self.markers:
            return self

        return RootConfig(markers=(*self.markers, marker))

    def removeMarker(self, marker: str) -> "RootConfig":
        """
        Removes a root marker.

        :param marker: str = Marker value

        :return: RootConfig = New configuration instance

        :raises RootMarkerNotFoundError:
            When marker does not exist

        :example:
            >>> from infra_core.core.root.root_config import RootConfig
            >>> config = RootConfig().addMarker(".env")
            >>> config = config.removeMarker(".env")
            >>> ".env" in config.markers
            False
        """
        if marker not in self.markers:
            raise RootMarkerNotFoundError(marker)

        return RootConfig(markers=tuple(m for m in self.markers if m != marker))

    # ============================================================
    # Private Methods
    # ============================================================

    def _validateMarkers(self, markers: Tuple[str, ...]) -> None:
        """
        Validates all markers.

        :param markers: Tuple[str, ...]

        :return: None

        :raises InvalidRootMarkerError:
            When any marker is invalid
        """
        for marker in markers:
            self._validateMarker(marker)

    def _validateMarker(self, marker: str) -> None:
        """
        Validates a single marker.

        :param marker: str

        :return: None

        :raises InvalidRootMarkerError:
            When marker is invalid
        """
        if not isinstance(marker, str) or not marker:
            raise InvalidRootMarkerError(str(marker))

    def _defaultMarkers(self) -> Tuple[str, ...]:
        """
        Returns default root markers.

        :return: Tuple[str, ...] = Default markers

        :example:
            >>> from infra_core.core.root.root_config import RootConfig
            >>> config = RootConfig()
            >>> isinstance(config._defaultMarkers(), tuple)
            True
        """
        return (
            ".git",
            "pyproject.toml",
            "requirements.txt",
            "venv",
            ".venv",
            ".root",
        )


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    try:
        config = RootConfig()
        print("Default markers:", config.markers)

        config = config.addMarker(".env")
        print("After add:", config.markers)

        config = config.removeMarker(".env")
        print("After remove:", config.markers)

        try:
            config.removeMarker(".unknown")
        except Exception as err:
            print("Expected error:", err)

    except Exception as error:
        print(error)
