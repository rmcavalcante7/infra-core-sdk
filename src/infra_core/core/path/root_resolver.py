# ============================================================
# Dependencies:
# - pathlib
# - inspect
# ============================================================

from pathlib import Path

from infra_core.core.path.path_config import PathConfig
from infra_core.core.path.exceptions import PathResolutionError


class RootResolver:
    """
    Responsible for resolving the project root directory.

    This class determines the root directory by traversing the filesystem
    and matching configured root markers.

    :example:
        >>> from pathlib import Path
        >>> from infra_core.core.path.path_config import PathConfig
        >>> resolver = RootResolver(PathConfig(root_markers=(), directories={}))
        >>> isinstance(resolver, RootResolver)
        True
    """

    def __init__(self, config: PathConfig) -> None:
        """
        Initialize RootResolver.

        :param config: PathConfig = Configuration containing root markers.

        :example:
            >>> from infra_core.core.path.path_config import PathConfig
            >>> resolver = RootResolver(PathConfig(root_markers=(), directories={}))
            >>> isinstance(resolver, RootResolver)
            True
        """
        self._config: PathConfig = config

    # ============================================================
    # Public Methods
    # ============================================================

    def resolve(self, start_path: Path) -> Path:
        """
        Resolve the project root directory.

        :param start_path: Path = Starting path for resolution.

        :return: Path = Resolved project root directory.

        :raises PathResolutionError:
            When resolution fails unexpectedly.

        :example:
            >>> from pathlib import Path
            >>> from infra_core.core.path.path_config import PathConfig
            >>> resolver = RootResolver(PathConfig(root_markers=(), directories={}))
            >>> isinstance(resolver.resolve(Path.cwd()), Path)
            True
        """
        try:
            current: Path = start_path.resolve()

            for parent in [current] + list(current.parents):
                if self._isRoot(parent):
                    return parent

            return Path.cwd()

        except Exception as exc:
            raise PathResolutionError(
                f"Class: {self.__class__.__name__}\n"
                f"Method: resolve\n"
                f"Error resolving root: {exc}"
            ) from exc

    # ============================================================
    # Helper Methods
    # ============================================================

    def _isRoot(self, path: Path) -> bool:
        """
        Determine whether a directory qualifies as project root.

        :param path: Path = Directory to evaluate.

        :return: bool = True if directory matches root markers.

        :example:
            >>> from pathlib import Path
            >>> from infra_core.core.path.path_config import PathConfig
            >>> resolver = RootResolver(PathConfig(root_markers=(), directories={}))
            >>> isinstance(resolver._isRoot(Path.cwd()), bool)
            True
        """
        return any((path / marker).exists() for marker in self._config.root_markers)
