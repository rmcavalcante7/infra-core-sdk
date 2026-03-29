# ============================================================
# Dependencies:
# - pathlib
# - shutil
# - typing
# ============================================================

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, Optional

from infra_core.core.path.path_config_provider import PathConfigProvider
from infra_core.core.path.exceptions import (
    PathNotFoundError,
    PathResolutionError,
)
from infra_core.core.root.root_resolver import RootResolver


class PathManager:
    """
    Runtime manager for path operations.

    Responsibilities:
    - Resolve paths
    - Create directories and files
    - Ensure path existence
    - Delete filesystem resources
    - Manage path configuration

    :example:
        >>> from infra_core.core.path.path_manager import PathManager
        >>> manager = PathManager()
        >>> isinstance(manager.getRoot(), Path)
        True
    """

    def __init__(self) -> None:
        """
        Initializes PathManager.

        :return: None

        :example:
            >>> from infra_core.core.path.path_manager import PathManager
            >>> manager = PathManager()
            >>> isinstance(manager, PathManager)
            True
        """
        self._root_resolver = RootResolver()
        self._root: Path = self._root_resolver.resolve()

    # ============================================================
    # Public Methods
    # ============================================================

    def getRoot(self) -> Path:
        """
        Returns the resolved project root.

        :return: Path = Root directory

        :example:
            >>> from infra_core.core.path.path_manager import PathManager
            >>> manager = PathManager()
            >>> isinstance(manager.getRoot(), Path)
            True
        """
        return self._root

    def getPath(
        self,
        key: str,
        name: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> Path:
        """
        Resolves a configured path.

        Supports:
        - Legacy `name`
        - Multiple `variables`

        :param key: str = Path identifier
        :param name: Optional[str] = Legacy variable
        :param variables: Optional[Dict[str, str]] = Template variables

        :return: Path = Resolved path

        :raises PathNotFoundError:
            When key does not exist

        :raises PathResolutionError:
            When resolution fails

        :example:
            >>> from infra_core.core.path.path_manager import PathManager
            >>> manager = PathManager()
            >>> try:
            ...     manager.getPath("unknown")
            ... except Exception:
            ...     True
            True
        """
        config = PathConfigProvider.get()

        if key not in config.paths:
            raise PathNotFoundError(key)

        definition = config.paths[key]

        try:
            return definition.resolve(
                self._root,
                name=name,
                variables=variables,
            )
        except Exception as exc:
            raise PathResolutionError(
                key,
                context={
                    "definition": definition.path,
                    "variables": variables,
                },
            ) from exc

    def createPath(
        self,
        key: str,
        name: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        is_file: bool = False,
    ) -> Path:
        """
        Creates a filesystem resource (directory or file).

        :param key: str = Path identifier
        :param name: Optional[str] = Legacy variable
        :param variables: Optional[Dict[str, str]] = Template variables
        :param is_file: bool = If True, creates a file

        :return: Path = Created path

        :raises PathResolutionError:
            When creation fails

        :example:
            >>> from infra_core.core.path.path_manager import PathManager
            >>> manager = PathManager()
            >>> try:
            ...     manager.createPath("unknown")
            ... except Exception:
            ...     True
            True
        """
        path = self.getPath(key, name=name, variables=variables)

        try:
            if is_file:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch(exist_ok=True)
            else:
                path.mkdir(parents=True, exist_ok=True)

            return path

        except Exception as exc:
            raise PathResolutionError(
                key,
                context={
                    "operation": "create",
                    "path": str(path),
                    "variables": variables,
                    "is_file": is_file,
                },
            ) from exc

    def ensurePathExists(
        self,
        key: str,
        name: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        is_file: bool = False,
    ) -> Path:
        """
        Ensures that a path exists. Creates it if necessary.

        :param key: str = Path identifier
        :param name: Optional[str] = Legacy variable
        :param variables: Optional[Dict[str, str]] = Template variables
        :param is_file: bool = If True, ensures file existence

        :return: Path = Existing or created path

        :raises PathResolutionError:
            When operation fails

        :example:
            >>> from infra_core.core.path.path_manager import PathManager
            >>> manager = PathManager()
            >>> try:
            ...     manager.ensurePathExists("unknown")
            ... except Exception:
            ...     True
            True
        """
        path = self.getPath(key, name=name, variables=variables)

        if path.exists():
            return path

        return self.createPath(
            key,
            name=name,
            variables=variables,
            is_file=is_file,
        )

    def deleteResource(
        self,
        key: str,
        name: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
        missing_ok: bool = True,
    ) -> None:
        """
        Deletes the filesystem resource associated with the path.

        This method deletes the actual file or directory.

        :param key: str = Path identifier
        :param name: Optional[str] = Legacy variable
        :param variables: Optional[Dict[str, str]] = Template variables
        :param missing_ok: bool = Ignore if resource does not exist

        :return: None

        :raises PathNotFoundError:
            When key does not exist

        :raises PathResolutionError:
            When deletion fails

        :example:
            >>> from infra_core.core.path.path_manager import PathManager
            >>> manager = PathManager()
            >>> try:
            ...     manager.deleteResource("unknown")
            ... except Exception:
            ...     True
            True
        """
        path = self.getPath(key, name=name, variables=variables)

        try:
            if not path.exists():
                if missing_ok:
                    return
                raise FileNotFoundError(str(path))

            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

        except Exception as exc:
            raise PathResolutionError(
                key,
                context={
                    "operation": "delete_resource",
                    "path": str(path),
                    "variables": variables,
                },
            ) from exc

    def removeFromConfig(self, key: str) -> None:
        """
        Removes a path definition from configuration.

        :param key: str = Path identifier

        :return: None

        :raises PathNotFoundError:
            When key does not exist

        :example:
            >>> from infra_core.core.path.path_manager import PathManager
            >>> manager = PathManager()
            >>> try:
            ...     manager.removeFromConfig("unknown")
            ... except Exception:
            ...     True
            True
        """
        config = PathConfigProvider.get()

        if key not in config.paths:
            raise PathNotFoundError(key)

        new_config = config.removePath(key)
        PathConfigProvider.set(new_config)


# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    from infra_core.core.path.path_definition import PathDefinition
    from infra_core.core.path.path_config_provider import PathConfigProvider
    from infra_core.core.root.root_resolver import RootResolver

    try:
        # --------------------------------------------------------
        # Resolve root
        # --------------------------------------------------------
        root = RootResolver().resolve()
        print("Resolved ROOT:", root)

        # --------------------------------------------------------
        # Setup config (multi-level path)
        # --------------------------------------------------------
        config = PathConfigProvider.get()

        config = config.addPath("logs_file", PathDefinition("logs/{dir}/{name}"))

        config = config.addPath("logs_root", PathDefinition("logs"))

        config = config.addPath("logs_legacy", PathDefinition("logs/{name}"))

        PathConfigProvider.set(config)

        manager = PathManager()

        # --------------------------------------------------------
        # Caso 1: Criar diretório raiz (logs/)
        # --------------------------------------------------------
        logs_root = manager.createPath("logs_root")
        print("Created logs root:", logs_root)

        # --------------------------------------------------------
        # Caso 2: Criar diretório (logs/app)
        # --------------------------------------------------------
        logs_dir = manager.createPath("logs_legacy", name="app")
        print("Created logs dir:", logs_dir)

        # --------------------------------------------------------
        # Caso 3: Criar arquivo (logs/app/file.txt) → variables
        # --------------------------------------------------------
        file_path = manager.createPath(
            "logs_file", variables={"dir": "app", "name": "file.txt"}, is_file=True
        )
        print("Created file:", file_path)

        # --------------------------------------------------------
        # Caso 4: Resolver path (sem criar)
        # --------------------------------------------------------
        resolved = manager.getPath(
            "logs_file", variables={"dir": "app", "name": "file.txt"}
        )
        print("Resolved path:", resolved)

        # --------------------------------------------------------
        # Caso 5: Ensure path exists
        # --------------------------------------------------------
        ensured = manager.ensurePathExists(
            "logs_file", variables={"dir": "app", "name": "file.txt"}, is_file=True
        )
        print("Ensured path:", ensured)

        # --------------------------------------------------------
        # Caso 6: Delete file
        # --------------------------------------------------------
        manager.deleteResource(
            "logs_file", variables={"dir": "app", "name": "file.txt"}
        )
        print("Deleted file")

        # --------------------------------------------------------
        # Caso 7: Delete directory
        # --------------------------------------------------------
        manager.deleteResource("logs_legacy", name="app")
        print("Deleted directory")

        # --------------------------------------------------------
        # Caso 8: Delete inexistente (não falha)
        # --------------------------------------------------------
        manager.deleteResource("logs_legacy", name="app", missing_ok=True)
        print("Delete missing (ignored)")

        # --------------------------------------------------------
        # Caso 9: Remover do config
        # --------------------------------------------------------
        manager.removeFromConfig("logs_file")
        print("Removed logs_file from config")

        # --------------------------------------------------------
        # Caso 10: Erro esperado
        # --------------------------------------------------------
        try:
            manager.getPath("logs_file")
        except Exception as err:
            print("Expected error:", err)

    except Exception as error:
        print("Unexpected error:", error)
