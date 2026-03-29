# ============================================================
# Dependencies:
# - dataclasses
# - typing
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from infra_core.core.path.path_definition import PathDefinition
from infra_core.core.path.exceptions import (
    PathAlreadyExistsError,
    PathNotFoundError,
    InvalidPathDefinitionError,
)


@dataclass(frozen=True)
class PathConfig:
    """
    Immutable configuration for path definitions.

    This class is responsible only for:
    - Storing path definitions
    - Validating inputs
    - Returning new instances on mutation

    It does NOT:
    - Resolve paths
    - Access filesystem
    - Handle root logic

    :param paths: Dict[str, PathDefinition] = Mapping of path keys to definitions

    :example:
        >>> from infra_core.core.path.path_config import PathConfig
        >>> from infra_core.core.path.path_definition import PathDefinition
        >>> from pathlib import Path

        >>> config = PathConfig()
        >>> config = config.addPath("logs", PathDefinition("logs"))
        >>> "logs" in config.paths
        True

        >>> # Caso: path absoluto fora do root
        >>> absolute_path = str(Path.cwd())
        >>> config = config.addPath("external", PathDefinition(absolute_path, use_root=False))
        >>> config.paths["external"].use_root
        False

        >>> # Caso inválido: path relativo com use_root=False
        >>> try:
        ...     PathDefinition("relative/path", use_root=False)
        ... except Exception:
        ...     True
        True
    """

    paths: Dict[str, PathDefinition] = field(default_factory=dict)

    # ============================================================
    # Public Methods
    # ============================================================

    def addPath(self, key: str, definition: PathDefinition) -> "PathConfig":
        """
        Adds a new path definition.

        :param key: str = Unique path identifier
        :param definition: PathDefinition = Path definition object

        :return: PathConfig = New configuration instance

        :raises PathAlreadyExistsError:
            When key already exists

        :raises InvalidPathDefinitionError:
            When definition is invalid

        :example:
            >>> from infra_core.core.path.path_config import PathConfig
            >>> from infra_core.core.path.path_definition import PathDefinition
            >>> config = PathConfig()
            >>> config = config.addPath("logs", PathDefinition("logs"))
            >>> "logs" in config.paths
            True
        """
        if key in self.paths:
            raise PathAlreadyExistsError(key)

        self._validateDefinition(key, definition)

        new_paths = dict(self.paths)
        new_paths[key] = definition

        return PathConfig(paths=new_paths)

    def updatePath(self, key: str, definition: PathDefinition) -> "PathConfig":
        """
        Updates an existing path definition.

        :param key: str = Path identifier
        :param definition: PathDefinition = New definition

        :return: PathConfig = New configuration instance

        :raises PathNotFoundError:
            When key does not exist

        :raises InvalidPathDefinitionError:
            When definition is invalid

        :example:
            >>> from infra_core.core.path.path_config import PathConfig
            >>> from infra_core.core.path.path_definition import PathDefinition
            >>> config = PathConfig().addPath("logs", PathDefinition("logs"))
            >>> config = config.updatePath("logs", PathDefinition("new_logs"))
            >>> config.paths["logs"].path
            'new_logs'
        """
        if key not in self.paths:
            raise PathNotFoundError(key)

        self._validateDefinition(key, definition)

        new_paths = dict(self.paths)
        new_paths[key] = definition

        return PathConfig(paths=new_paths)

    def removePath(self, key: str) -> "PathConfig":
        """
        Removes a path definition from configuration.

        :param key: str = Path identifier

        :return: PathConfig = New configuration instance

        :raises PathNotFoundError:
            When key does not exist

        :example:
            >>> from infra_core.core.path.path_config import PathConfig
            >>> from infra_core.core.path.path_definition import PathDefinition
            >>> config = PathConfig().addPath("logs", PathDefinition("logs"))
            >>> config = config.removePath("logs")
            >>> "logs" in config.paths
            False
        """
        if key not in self.paths:
            raise PathNotFoundError(key)

        new_paths = dict(self.paths)
        del new_paths[key]

        return PathConfig(paths=new_paths)

    # ============================================================
    # Private Methods
    # ============================================================

    def _validateDefinition(self, key: str, definition: PathDefinition) -> None:
        """
        Validates a path definition.

        :param key: str = Path identifier
        :param definition: PathDefinition

        :raises InvalidPathDefinitionError:
            When definition is invalid
        """
        if not isinstance(definition, PathDefinition):
            raise InvalidPathDefinitionError(
                key=key,
                path=str(definition),
            )

    # ============================================================
    # Utility Methods
    # ============================================================

    def hasPath(self, key: str) -> bool:
        """
        Checks if a path exists.

        :param key: str

        :return: bool = True if exists

        :example:
            >>> from infra_core.core.path.path_config import PathConfig
            >>> config = PathConfig()
            >>> config.hasPath("logs")
            False
        """
        return key in self.paths


# ============================================================
# Main (Usage Example)
# ============================================================

# ============================================================
# Main (Usage Example)
# ============================================================

if __name__ == "__main__":
    from pathlib import Path
    from infra_core.core.path.path_definition import PathDefinition
    from infra_core.core.root.root_resolver import RootResolver

    try:
        config = PathConfig()

        # --------------------------------------------------------
        # Caso 1: Path relativo (usa root)
        # --------------------------------------------------------
        config = config.addPath("logs", PathDefinition("logs"))
        print("After add (relative):", config.paths)

        # 🔥 RESOLUÇÃO REAL COM ROOT
        root = RootResolver().resolve()
        resolved_logs = config.paths["logs"].resolve(root, name="app")
        print("Resolved (use_root=True):", resolved_logs)

        # --------------------------------------------------------
        # Caso 2: Update
        # --------------------------------------------------------
        config = config.updatePath("logs", PathDefinition("new_logs"))
        print("After update:", config.paths)

        # --------------------------------------------------------
        # Caso 3: Path absoluto (fora do root)
        # --------------------------------------------------------
        absolute_path = str(Path.cwd())
        config = config.addPath(
            "external",
            PathDefinition(absolute_path, use_root=False),
        )
        print("After add (absolute):", config.paths)

        resolved_external = config.paths["external"].resolve(root)
        print("Resolved (use_root=False):", resolved_external)

        # --------------------------------------------------------
        # Caso 4: Remoção
        # --------------------------------------------------------
        config = config.removePath("logs")
        print("After remove:", config.paths)

        # --------------------------------------------------------
        # Caso 5: Erro esperado
        # --------------------------------------------------------
        try:
            PathDefinition("invalid/path", use_root=False)
        except Exception as err:
            print("Expected error:", err)

    except Exception as error:
        print(error)
