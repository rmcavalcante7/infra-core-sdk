# ============================================================
# Dependencies:
# - pathlib
# ============================================================

from __future__ import annotations

from pathlib import Path

from infra_core.core.root.root_config_provider import RootConfigProvider
from infra_core.core.root.exceptions import RootResolutionError


class RootResolver:
    """
    Resolves the project root directory using configured markers.

    This class:
    - Retrieves markers from RootConfigProvider
    - Traverses the directory tree upwards
    - Finds the first directory matching a root marker

    Resolution is cached after the first successful call.

    :example:
        >>> from infra_core.core.root.root_resolver import RootResolver
        >>> resolver = RootResolver()
        >>> root = resolver.resolve()
        >>> isinstance(root, Path)
        True
    """

    def __init__(self) -> None:
        """
        Initializes RootResolver.

        :return: None

        :example:
            >>> from infra_core.core.root.root_resolver import RootResolver
            >>> resolver = RootResolver()
            >>> isinstance(resolver, RootResolver)
            True
        """
        self._root: Path | None = None

    # ============================================================
    # Public Methods
    # ============================================================

    def resolve(self) -> Path:
        """
        Resolves the project root directory.

        The resolution process:
        - Starts from current working directory
        - Traverses parent directories
        - Stops when a directory containing any configured marker is found

        :return: Path = Root directory

        :raises RootResolutionError:
            When root cannot be determined

        :example:
            >>> from infra_core.core.root.root_resolver import RootResolver
            >>> resolver = RootResolver()
            >>> isinstance(resolver.resolve(), Path)
            True
        """
        if self._root is not None:
            return self._root

        try:
            config = RootConfigProvider.get()
            markers = config.markers

            current = Path.cwd().resolve()

            for parent in [current] + list(current.parents):
                if self._isRoot(parent, markers):
                    self._root = parent
                    return parent

            raise RootResolutionError(
                message="Root directory not found",
                context={
                    "start_path": str(current),
                    "markers": markers,
                },
            )

        except Exception as exc:
            raise RootResolutionError(
                message="Failed to resolve root",
                context={"error": str(exc)},
            ) from exc

    # ============================================================
    # Private Methods
    # ============================================================

    def _isRoot(self, path: Path, markers: tuple[str, ...]) -> bool:
        """
        Checks whether a directory matches root criteria.

        :param path: Path = Directory to evaluate
        :param markers: tuple[str, ...] = Root markers

        :return: bool = True if directory is root

        :example:
            >>> from pathlib import Path
            >>> from infra_core.core.root.root_resolver import RootResolver
            >>> resolver = RootResolver()
            >>> isinstance(resolver._isRoot(Path.cwd(), (".git",)), bool)
            True
        """
        return any((path / marker).exists() for marker in markers)


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    try:
        resolver = RootResolver()
        root = resolver.resolve()

        print("Resolved root:", root)

        # Demonstrate caching
        root_again = resolver.resolve()
        print("Resolved root (cached):", root_again)

    except Exception as error:
        print(error)
