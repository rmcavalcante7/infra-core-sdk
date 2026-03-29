# ============================================================
# Dependencies:
# - dataclasses
# - pathlib
# - typing
# - re
# ============================================================

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from infra_core.core.path.exceptions import InvalidPathDefinitionError


@dataclass(frozen=True)
class PathDefinition:
    """
    Represents a path definition with template support.

    Supports dynamic placeholders using `{variable}` syntax.

    Examples:
    - "logs/{name}"
    - "logs/{dir}/{name}"

    :param path: str = Path template
    :param use_root: bool = Whether to resolve relative to root

    :raises InvalidPathDefinitionError:
        When path is invalid

    :example:
        >>> from infra_core.core.path.path_definition import PathDefinition
        >>> definition = PathDefinition("logs/{name}")
        >>> isinstance(definition.path, str)
        True
    """

    path: str
    use_root: bool = True

    # ============================================================
    # Initialization
    # ============================================================

    def __post_init__(self) -> None:
        """
        Validates path definition.

        :return: None

        :raises InvalidPathDefinitionError:

        :example:
            >>> from infra_core.core.path.path_definition import PathDefinition
            >>> try:
            ...     PathDefinition("")
            ... except Exception:
            ...     True
            True
        """
        self._validate()

    # ============================================================
    # Public Methods
    # ============================================================

    def resolve(
        self,
        root: Path,
        name: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> Path:
        """
        Resolves the final path using variables.

        Supports:
        - Legacy `name`
        - Multiple variables

        :param root: Path = Root directory
        :param name: Optional[str] = Backward compatibility variable
        :param variables: Optional[Dict[str, str]] = Template variables

        :return: Path

        :raises InvalidPathDefinitionError:
            When variables are missing or invalid

        :example:
            >>> from pathlib import Path
            >>> from infra_core.core.path.path_definition import PathDefinition
            >>> definition = PathDefinition("logs/{name}")
            >>> result = definition.resolve(Path("/tmp"), name="app")
            >>> isinstance(result, Path)
            True
        """
        try:
            final_variables: Dict[str, str] = {}

            # Backward compatibility
            if name is not None:
                final_variables["name"] = name

            if variables:
                final_variables.update(variables)

            placeholders = self._extractPlaceholders()

            # Validate all placeholders are provided
            missing = [p for p in placeholders if p not in final_variables]

            if missing:
                raise InvalidPathDefinitionError(
                    key="unknown",
                    path=f"Missing variables: {missing}",
                )

            path_str = self.path

            for key, value in final_variables.items():
                path_str = path_str.replace(f"{{{key}}}", value)

            if self.use_root:
                return root / path_str

            return Path(path_str)

        except Exception as exc:
            raise InvalidPathDefinitionError(
                key="unknown",
                path=self.path,
            ) from exc

    # ============================================================
    # Private Methods
    # ============================================================

    def _validate(self) -> None:
        """
        Validates path structure.

        :raises InvalidPathDefinitionError:
        """
        if not isinstance(self.path, str) or not self.path:
            raise InvalidPathDefinitionError(
                key="unknown",
                path=str(self.path),
            )

        if not self.use_root:
            if not Path(self.path).is_absolute():
                raise InvalidPathDefinitionError(
                    key="unknown",
                    path=self.path,
                )

    def _extractPlaceholders(self) -> list[str]:
        """
        Extracts placeholders from template.

        :return: list[str]

        :example:
            >>> from infra_core.core.path.path_definition import PathDefinition
            >>> d = PathDefinition("logs/{dir}/{name}")
            >>> "dir" in d._extractPlaceholders()
            True
        """
        return re.findall(r"{(.*?)}", self.path)


# ============================================================
# Main (Usage Example)
# ============================================================
if __name__ == "__main__":
    from infra_core.core.root.root_resolver import RootResolver
    from pathlib import Path

    try:
        resolver = RootResolver()
        root = resolver.resolve()

        print("Resolved ROOT:", root)

        definition = PathDefinition("logs/{dir}/{name}")

        resolved = definition.resolve(
            root,
            variables={"dir": "app", "name": "file.txt"},
        )

        print("Resolved:", resolved)

        # Backward compatibility
        definition_legacy = PathDefinition("logs/{name}")
        resolved_legacy = definition_legacy.resolve(
            root,
            name="app",
        )

        print("Resolved legacy:", resolved_legacy)

        # Error case
        try:
            definition.resolve(root, variables={"dir": "app"})
        except Exception as err:
            print("Expected error:", err)

    except Exception as error:
        print(error)
