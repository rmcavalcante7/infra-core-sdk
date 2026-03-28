# ============================================================
# Dependencies:
# - dataclasses
# - typing
# - inspect
# ============================================================

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from infra_core.core.path import exceptions


# ============================================================
# Core Data Structure
# ============================================================

@dataclass(frozen=True)
class PathConfig:
    """
    Immutable configuration object defining path resolution behavior.

    This class provides:
    - Dynamic directory dependency resolution
    - Global synchronized configuration
    - Strong validation and domain-specific exceptions

    :param root_markers: Optional[Tuple[str, ...]] = Root detection markers
    :param directories: Optional[Dict[str, str]] = Directory mapping overrides

    :example:
        >>> config = PathConfig()
        >>> config.directories[config.secretDirKey]
        'secret'
    """

    root_markers: Optional[Tuple[str, ...]] = None

    _secret_dir_name: str = field(default="secret_dir", repr=False)
    _secret_key_name: str = field(default="secret_key", repr=False)
    _credentials_dir_name: str = field(default="credentials", repr=False)
    _download_dir_name: str = field(default="downloads", repr=False)

    directories: Optional[Dict[str, str]] = None

    _default_instance: PathConfig = None

    # ============================================================
    # Initialization
    # ============================================================

    def __post_init__(self) -> None:
        """
        Initializes root markers and directory mappings.

        :raises PathValidationError:
            When configuration is invalid

        :example:
            >>> config = PathConfig()
            >>> isinstance(config.directories, dict)
            True
        """
        try:
            self._validateKeys()

            # Root markers
            if self.root_markers is None:
                object.__setattr__(
                    self,
                    "root_markers",
                    self._buildDefaultRootMarkers(),
                )
            else:
                self._validateRootMarkers(self.root_markers)

            # Directories (dependency-aware)
            base_dir: str = (
                self.directories.get(self._secret_dir_name)
                if self.directories and self._secret_dir_name in self.directories
                else "secret"
            )

            directories: Dict[str, str] = self._buildDependentDirectories(base_dir)

            if self.directories:
                for key, value in self.directories.items():
                    if key not in directories:
                        directories[key] = value

            object.__setattr__(self, "directories", directories)

        except exceptions.PathConfigError:
            raise

        except Exception as exc:
            raise exceptions.PathValidationError(
                self._buildError(str(exc))
            ) from exc

    # ============================================================
    # Properties
    # ============================================================

    @property
    def secretDirKey(self) -> str:
        """
        Returns secret directory key.

        :return: str

        :example:
            >>> PathConfig().secretDirKey
            'secret_dir'
        """
        return self._secret_dir_name

    @property
    def secretKeyKey(self) -> str:
        """
        Returns secret key key.

        :return: str

        :example:
            >>> PathConfig().secretKeyKey
            'secret_key'
        """
        return self._secret_key_name

    @property
    def credentialsDir(self) -> str:
        """
        Returns credentials key.

        :return: str

        :example:
            >>> PathConfig().credentialsDir
            'credentials'
        """
        return self._credentials_dir_name

    @property
    def downloadKey(self) -> str:
        """
        Returns download key.

        :return: str

        :example:
            >>> PathConfig().downloadKey
            'downloads'
        """
        return self._download_dir_name

    # ============================================================
    # Public API - Directories
    # ============================================================

    def addDirectory(self, key: str, path: str) -> PathConfig:
        """
        Adds a new independent directory mapping.

        :param key: str = Directory key
        :param path: str = Directory path
        :return: PathConfig

        :raises DirectoryAlreadyExistsError:
            When key already exists

        :raises InvalidDirectoryPathError:
            When path is invalid

        :example:
            >>> config = PathConfig()
            >>> config = config.addDirectory("logs", "logs")
        """
        if key in self.directories:
            raise exceptions.DirectoryAlreadyExistsError(key)

        if not path:
            raise exceptions.InvalidDirectoryPathError(key, path)

        new_dirs = dict(self.directories)
        new_dirs[key] = path

        new_config = PathConfig(
            root_markers=self.root_markers,
            directories=new_dirs,
        )

        self.__class__._setAsDefault(new_config)
        return new_config

    def updateDirectory(self, key: str, path: str) -> PathConfig:
        """
        Updates a directory and propagates dependency recalculation.

        :param key: str = Directory key
        :param path: str = New path
        :return: PathConfig

        :raises DirectoryNotFoundError:
            When key does not exist

        :raises InvalidDirectoryPathError:
            When path is invalid

        :example:
            >>> config = PathConfig()
            >>> config = config.updateDirectory("secret_dir", "new_secret")
        """
        if key not in self.directories:
            raise exceptions.DirectoryNotFoundError(key)

        if not path:
            raise exceptions.InvalidDirectoryPathError(key, path)

        new_dirs = dict(self.directories)
        new_dirs[key] = path

        new_config = PathConfig(
            root_markers=self.root_markers,
            directories=new_dirs,
        )

        self.__class__._setAsDefault(new_config)
        return new_config

    # ============================================================
    # Public API - Root Markers
    # ============================================================

    def addRootMarker(self, marker: str) -> PathConfig:
        """
        Adds a root marker.

        :param marker: str
        :return: PathConfig

        :raises InvalidRootMarkerError:
            When marker is invalid

        :example:
            >>> config = PathConfig()
            >>> config = config.addRootMarker(".custom")
        """
        if not marker or not isinstance(marker, str):
            raise exceptions.InvalidRootMarkerError(marker)

        if marker in self.root_markers:
            return self

        new_config = PathConfig(
            root_markers=(*self.root_markers, marker),
            directories=self.directories,
        )

        self.__class__._setAsDefault(new_config)
        return new_config

    def removeRootMarker(self, marker: str) -> PathConfig:
        """
        Removes a root marker.

        :param marker: str
        :return: PathConfig

        :raises RootMarkerNotFoundError:
            When marker does not exist

        :example:
            >>> config = PathConfig()
            >>> config = config.removeRootMarker(".git")
        """
        if marker not in self.root_markers:
            raise exceptions.RootMarkerNotFoundError(marker)

        new_config = PathConfig(
            root_markers=tuple(m for m in self.root_markers if m != marker),
            directories=self.directories,
        )

        self.__class__._setAsDefault(new_config)
        return new_config

    @classmethod
    def getDefault(cls) -> PathConfig:
        """
        Returns the current default configuration.

        :return: PathConfig

        :example:
            >>> config = PathConfig.getDefault()
        """
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

    # ============================================================
    # Helper Methods
    # ============================================================

    def _validateKeys(self) -> None:
        """
        Validates internal keys.

        :raises PathValidationError:
            When keys are invalid

        :example:
            >>> PathConfig()._validateKeys()
        """
        if not all(
            isinstance(v, str) and v
            for v in (
                self._secret_dir_name,
                self._secret_key_name,
                self._credentials_dir_name,
                self._download_dir_name,
            )
        ):
            raise exceptions.PathValidationError(
                self._buildError("Invalid internal keys")
            )

    def _validateRootMarkers(self, markers: Tuple[str, ...]) -> None:
        """
        Validates root markers.

        :param markers: Tuple[str, ...]

        :raises InvalidRootMarkerError:
            When markers are invalid

        :example:
            >>> PathConfig()._validateRootMarkers((".git",))
        """
        if not all(isinstance(m, str) and m for m in markers):
            raise exceptions.InvalidRootMarkerError(str(markers))

    def _buildDependentDirectories(self, base_dir: str) -> Dict[str, str]:
        """
        Builds dependent directory structure.

        :param base_dir: str
        :return: Dict[str, str]

        :example:
            >>> config = PathConfig()
            >>> config._buildDependentDirectories("x")["secret_key"]
            'x/secret.key'
        """
        return {
            self._secret_dir_name: base_dir,
            self._secret_key_name: f"{base_dir}/secret.key",
            self._credentials_dir_name: f"{base_dir}/{{name}}.json",
            self._download_dir_name: "downloads",
        }

    def _buildDefaultRootMarkers(self) -> Tuple[str, ...]:
        """
        Builds default root markers.

        :return: Tuple[str, ...]

        :example:
            >>> ".git" in PathConfig()._buildDefaultRootMarkers()
            True
        """
        return (
            ".git",
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            ".root",
            ".venv",
            "venv",
        )

    def _buildError(self, message: str) -> str:
        """
        Builds standardized error message with context.

        :param message: str
        :return: str

        :example:
            >>> config = PathConfig()
            >>> "Class" in config._buildError("x")
            True
        """
        return (
            f"Class: {self.__class__.__name__}\n"
            f"Method: {inspect.currentframe().f_back.f_code.co_name}\n"
            f"Error: {message}"
        )

    @classmethod
    def _setAsDefault(cls, config: PathConfig) -> None:
        """
        Sets global default configuration.

        :param config: PathConfig

        :example:
            >>> config = PathConfig()
            >>> PathConfig._setAsDefault(config)
        """
        cls._default_instance = config


# ============================================================
# Default Configuration (Proxy)
# ============================================================

class _DefaultPathConfigProxy:
    """
    Proxy object that always resolves the latest PathConfig instance.

    :example:
        >>> config = DEFAULT_PATH_CONFIG
        >>> isinstance(config.directories, dict)
        True
    """

    def __getattr__(self, item):
        return getattr(PathConfig.getDefault(), item)

    def __repr__(self):
        return repr(PathConfig.getDefault())


DEFAULT_PATH_CONFIG = _DefaultPathConfigProxy()


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    config = DEFAULT_PATH_CONFIG

    print("Roots:", config.root_markers)
    print("Dirs:", config.directories)

    config = config.addDirectory("logs", "logs")
    print("After add dir:", config.directories)

    config = config.updateDirectory(config.downloadKey, "new_downloads")
    print("After update dir:", config.directories)

    config = config.updateDirectory(config.secretDirKey, "new_secret")
    print("After update dir:", config.directories)

    config = config.addRootMarker(".custom")
    print("After add root:", config.root_markers)

    config = config.removeRootMarker(".custom")
    print("After remove root:", config.root_markers)