# ============================================================
# Dependencies:
# - dataclasses
# - pathlib
# - typing
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

from infra_core.core.root.exceptions import (
    InvalidRootStartPathError,
    InvalidRootMarkerError,
    RootMarkerNotFoundError,
)


@dataclass(frozen=True)
class RootConfig:
    """
    Immutable configuration for root resolution.

    Defines which markers are used to identify the project root.

    :param markers: Tuple[str, ...] = Root detection markers
    :param start_path: Optional[Path] = Preferred starting point for resolution

    :example:
        >>> from infra_core.core.root.root_config import RootConfig
        >>> config = RootConfig()
        >>> isinstance(config.markers, tuple)
        True
    """

    markers: Tuple[str, ...] = field(default_factory=tuple)
    start_path: Optional[Path] = None

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

        if self.start_path is not None:
            object.__setattr__(
                self,
                "start_path",
                self._normalizeStartPath(self.start_path),
            )

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

        return RootConfig(
            markers=(*self.markers, marker),
            start_path=self.start_path,
        )

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

        return RootConfig(
            markers=tuple(m for m in self.markers if m != marker),
            start_path=self.start_path,
        )

    def withStartPath(self, start_path: Path | str) -> "RootConfig":
        """
        Returns a new configuration with an explicit resolution start path.

        :param start_path: Path | str = Preferred starting point for root lookup

        :return: RootConfig = New configuration instance

        :raises InvalidRootStartPathError:
            When start_path is empty or invalid

        :example:
            >>> from pathlib import Path
            >>> from infra_core.core.root.root_config import RootConfig
            >>> config = RootConfig().withStartPath(Path.cwd())
            >>> isinstance(config.start_path, Path)
            True
        """
        return RootConfig(
            markers=self.markers,
            start_path=self._normalizeStartPath(start_path),
        )

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

    def _normalizeStartPath(self, start_path: Path | str) -> Path:
        """
        Normalizes configured start path into a resolved directory path.

        :param start_path: Path | str = Raw configured start path

        :return: Path = Normalized directory path

        :raises InvalidRootStartPathError:
            When start_path is empty or invalid
        """
        if isinstance(start_path, Path):
            normalized = start_path
        elif isinstance(start_path, str) and start_path.strip():
            normalized = Path(start_path)
        else:
            raise InvalidRootStartPathError(str(start_path))

        resolved = normalized.expanduser().resolve()

        if resolved.is_file():
            return resolved.parent

        return resolved


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
