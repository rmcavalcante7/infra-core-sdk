# ============================================================
# Dependencies:
# - pathlib
# - typing
# - inspect
# ============================================================

from pathlib import Path

from infra_core.core.path.path_config import PathConfig
from infra_core.core.path.root_resolver import RootResolver
from infra_core.core.path.exceptions import PathResolutionError


class PathManager:
    """
    High-level manager responsible for resolving project paths dynamically.

    :example:
        >>> from infra_core.core.path.path_config import PathConfig
        >>> config = PathConfig(root_markers=(), directories={"data": "data"})
        >>> manager = PathManager(config)
        >>> isinstance(manager.getRoot(), Path)
        True
    """

    def __init__(self, config: PathConfig) -> None:
        """
        Initialize PathManager.

        :param config: PathConfig = Configuration object

        :raises PathResolutionError:
            When initialization fails

        :example:
            >>> from infra_core.core.path.path_config import PathConfig
            >>> config = PathConfig(root_markers=(), directories={})
            >>> manager = PathManager(config)
            >>> isinstance(manager, PathManager)
            True
        """
        try:
            self._config: PathConfig = config
            # self._root: Path = RootResolver(config).resolve(Path(__file__))
            self._root: Path = RootResolver(config).resolve(Path.cwd())
        except Exception as exc:
            raise PathResolutionError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: __init__\n"
                f"Error initializing PathManager: {exc}"
            ) from exc

    # ============================================================
    # Public Methods
    # ============================================================

    def getPath(self, key: str, name: str | None = None) -> Path:
        """
        Resolve a filesystem path based on a configured key and optional name.

        This method retrieves a path template from configuration and optionally
        replaces the `{name}` placeholder when provided. It supports both static
        and dynamic path resolution.

        :param key: str = Key defined in PathConfig directories mapping
        :param name: str | None = Optional identifier used to replace `{name}` in path template

        :return: Path = Fully resolved filesystem path

        :raises KeyError:
            When the provided key does not exist in configuration

        :raises PathResolutionError:
            When path resolution fails
        """
        try:
            if key not in self._config.directories:
                raise KeyError(f"Invalid path key: {key}")

            path_template: str = self._config.directories[key]

            if name:
                path_template = path_template.replace("{name}", name)

            return self._root / path_template

        except KeyError:
            raise

        except Exception as exc:
            raise PathResolutionError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: getPath\n"
                f"Error resolving path: {exc}"
            ) from exc

    def getRoot(self) -> Path:
        """
        Retrieve project root.

        :return: Path = Root directory

        :example:
            >>> from infra_core.core.path.path_config import PathConfig
            >>> config = PathConfig(root_markers=(), directories={})
            >>> manager = PathManager(config)
            >>> isinstance(manager.getRoot(), Path)
            True
        """
        return self._root


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    from infra_core.core.path.path_config import DEFAULT_PATH_CONFIG

    manager = PathManager(PathConfig.getDefault())

    print("Root:", manager.getRoot())
    print("Credentials:", manager.getPath("credentials"))
