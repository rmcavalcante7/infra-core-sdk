# ============================================================
# Dependencies:
# - inspect
# - pathlib
# - typing
# ============================================================

from __future__ import annotations

import inspect
from pathlib import Path
import sys
from typing import Optional

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
            candidates = self._getStartCandidates(config.start_path)

            for candidate in candidates:
                for parent in [candidate] + list(candidate.parents):
                    if self._isRoot(parent, markers):
                        self._root = parent
                        return parent

            raise RootResolutionError(
                message="Root directory not found",
                context={
                    "start_paths": [str(candidate) for candidate in candidates],
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

    def _getStartCandidates(self, configured_start_path: Optional[Path]) -> list[Path]:
        """
        Returns candidate starting paths for root resolution.

        Resolution priority:
        - Explicitly configured start path
        - Current working directory
        - First caller frame outside the SDK package

        :param configured_start_path: Optional[Path] = Preferred configured path

        :return: list[Path] = Ordered unique candidate paths
        """
        candidates: list[Path] = []

        if configured_start_path is not None:
            candidates.append(configured_start_path)

        candidates.append(Path.cwd().resolve())

        if self._shouldUseCallerFallback():
            caller_path = self._getCallerPath()
            if caller_path is not None:
                candidates.append(caller_path)

        unique_candidates: list[Path] = []
        seen: set[Path] = set()

        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def _shouldUseCallerFallback(self) -> bool:
        """
        Determines whether caller-path fallback should be used.

        The fallback is intended for installed-package scenarios, where the
        SDK lives in `site-packages` and the process current directory may not
        match the consumer project's location.

        :return: bool = True when the SDK is running from an installed package
        """
        package_path = Path(__file__).resolve()
        package_parts = {part.lower() for part in package_path.parts}

        return "site-packages" in package_parts or "dist-packages" in package_parts

    def _getCallerPath(self) -> Optional[Path]:
        """
        Returns the first caller path outside the SDK package.

        :return: Optional[Path] = Caller directory path when available
        """
        package_root = Path(__file__).resolve().parents[2]
        main_path = self._getMainModulePath(package_root)
        if main_path is not None:
            return main_path

        for frame_info in reversed(inspect.stack()):
            frame_path = self._resolveFramePath(frame_info.filename)

            if frame_path is None:
                continue

            if self._isSdkPath(frame_path, package_root):
                continue

            if self._isPythonRuntimePath(frame_path):
                continue

            return frame_path.parent if frame_path.is_file() else frame_path

        return None

    def _getMainModulePath(self, package_root: Path) -> Optional[Path]:
        """
        Returns the path for the main module when available.

        :param package_root: Path = SDK package root path

        :return: Optional[Path] = Main module directory path
        """
        for frame_info in reversed(inspect.stack()):
            module_name = frame_info.frame.f_globals.get("__name__")
            frame_path = self._resolveFramePath(frame_info.filename)

            if module_name != "__main__" or frame_path is None:
                continue

            if self._isSdkPath(frame_path, package_root):
                continue

            return frame_path.parent if frame_path.is_file() else frame_path

        return None

    def _resolveFramePath(self, filename: str) -> Optional[Path]:
        """
        Resolves a frame filename into a filesystem path.

        :param filename: str = Frame filename

        :return: Optional[Path] = Resolved path when valid
        """
        if not filename:
            return None

        try:
            return Path(filename).resolve()
        except OSError:
            return None

    def _isSdkPath(self, frame_path: Path, package_root: Path) -> bool:
        """
        Checks whether a frame path belongs to the SDK package.

        :param frame_path: Path = Candidate frame path
        :param package_root: Path = SDK package root

        :return: bool = True when the frame belongs to the SDK package
        """
        return package_root in frame_path.parents or frame_path == package_root

    def _isPythonRuntimePath(self, frame_path: Path) -> bool:
        """
        Checks whether a frame belongs to the Python runtime or site-packages.

        :param frame_path: Path = Candidate frame path

        :return: bool = True when the frame belongs to Python runtime internals
        """
        frame_parts = {part.lower() for part in frame_path.parts}
        runtime_root = Path(sys.executable).resolve().parents[1]

        if runtime_root in frame_path.parents:
            return True

        return "site-packages" in frame_parts or "dist-packages" in frame_parts


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
