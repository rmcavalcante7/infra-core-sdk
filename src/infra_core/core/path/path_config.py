# ============================================================
# Dependencies:
# - dataclasses
# - typing
# - inspect
# ============================================================

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Dict, Tuple, ClassVar, Optional
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

    :param root_markers: root_markers: Tuple[str, ...] = field(default_factory=tuple) = Root detection markers
    :param directories: Dict[str, str] = field(default_factory=dict) = Directory mapping overrides

    :example:
        >>> config = PathConfig()
        >>> config.directories[config.secretDirKey]
        'secret'
    """

    root_markers: Tuple[str, ...] = field(default_factory=tuple)

    _secret_dir_name: str = field(default="secret_dir", repr=False)
    _secret_key_name: str = field(default="secret_key", repr=False)
    _credentials_dir_name: str = field(default="credentials", repr=False)
    _download_dir_name: str = field(default="downloads", repr=False)

    directories: Dict[str, str] = field(default_factory=dict)

    _default_instance: ClassVar[Optional["PathConfig"]] = None

    # ============================================================
    # Initialization
    # ============================================================

    def __post_init__(self) -> None:
        """
        Initializes root markers and directory mappings with dependency-aware resolution.

        Resolution rules:
        - User-provided directories are the source of truth
        - Dependent directories are recalculated based on secret_dir
        - Explicit user overrides are always respected
        - No directory is silently overridden

        :raises PathValidationError:
            When configuration is invalid

        :example:
            >>> config = PathConfig()
            >>> isinstance(config.directories, dict)
            True
        """
        try:
            # ============================================================
            # Validate internal keys
            # ============================================================
            self._validateKeys()

            # ============================================================
            # Root markers
            # ============================================================
            if not self.root_markers:
                object.__setattr__(
                    self,
                    "root_markers",
                    self._buildDefaultRootMarkers(),
                )
            else:
                self._validateRootMarkers(self.root_markers)

            # ============================================================
            # Directories
            # ============================================================

            input_dirs: Dict[str, str] = {
                self._secret_dir_name: "secret",
                self._download_dir_name: "downloads",
                **self.directories,
            }

            # 1. Resolve base_dir
            base_dir: str = input_dirs.get(self._secret_dir_name, "secret")

            # 2. Compute derived
            derived_dirs: Dict[str, str] = self._buildDependentDirectories(base_dir)

            # 3. Final começa com input
            final_dirs: Dict[str, str] = dict(input_dirs)

            # 4. Corrigir derivados
            for key in (self._secret_key_name, self._credentials_dir_name):
                current_value = input_dirs.get(key)

                expected_old = self._buildDependentDirectories("secret")[key]
                expected_new = derived_dirs[key]

                # Se o valor atual ainda segue o padrão antigo → recalcula
                if current_value == expected_old:
                    final_dirs[key] = expected_new

                # Se usuário não definiu → também calcula
                elif current_value is None:
                    final_dirs[key] = expected_new

                # senão: usuário sobrescreveu → respeita

            # 5. Guarantee base_dir consistency
            final_dirs[self._secret_dir_name] = base_dir

            object.__setattr__(self, "directories", final_dirs)

        except exceptions.PathConfigError:
            raise

        except Exception as exc:
            raise exceptions.PathValidationError(self._buildError(str(exc))) from exc

    def _getDerivedKeys(self) -> Tuple[str, ...]:
        return (
            self._secret_key_name,
            self._credentials_dir_name,
        )

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
        """
        frame = inspect.currentframe()

        method = (
            frame.f_back.f_code.co_name
            if frame is not None and frame.f_back is not None
            else "unknown"
        )

        return (
            f"Class: {self.__class__.__name__}\n"
            f"Method: {method}\n"
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

    def __getattr__(self, item: str) -> object:
        return getattr(PathConfig.getDefault(), item)

    def __repr__(self) -> str:
        return repr(PathConfig.getDefault())


DEFAULT_PATH_CONFIG = _DefaultPathConfigProxy()


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    config = PathConfig.getDefault()
    print(f"{config.root_markers=}")
    print(f"{config.directories=}")

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
