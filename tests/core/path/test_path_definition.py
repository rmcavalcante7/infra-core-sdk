# ============================================================
# Dependencies:
# - pytest
# - pathlib
# ============================================================

from pathlib import Path
import pytest

from infra_core.core.path.path_definition import PathDefinition
from infra_core.core.path.exceptions import InvalidPathDefinitionError

# ============================================================
# Tests
# ============================================================


def test_valid_path_definition():
    definition = PathDefinition("logs/{name}")

    assert definition.path == "logs/{name}"
    assert definition.use_root is True


def test_invalid_empty_path():
    with pytest.raises(InvalidPathDefinitionError):
        PathDefinition("")


def test_extract_placeholders():
    definition = PathDefinition("logs/{dir}/{name}")

    placeholders = definition._extractPlaceholders()

    assert "dir" in placeholders
    assert "name" in placeholders


def test_resolve_with_name():
    definition = PathDefinition("logs/{name}")

    root = Path("/tmp")

    result = definition.resolve(root, name="app")

    assert result.parts[-2:] == ("logs", "app")


def test_resolve_with_variables():
    definition = PathDefinition("logs/{dir}/{name}")

    root = Path("/tmp")

    result = definition.resolve(
        root,
        variables={"dir": "app", "name": "file.txt"},
    )

    assert result.parts[-3:] == ("logs", "app", "file.txt")


def test_resolve_missing_variable():
    definition = PathDefinition("logs/{dir}/{name}")

    root = Path("/tmp")

    with pytest.raises(InvalidPathDefinitionError):
        definition.resolve(root, variables={"dir": "app"})


def test_resolve_with_name_and_variables():
    definition = PathDefinition("logs/{dir}/{name}")

    root = Path("/tmp")

    result = definition.resolve(
        root,
        name="file.txt",
        variables={"dir": "app"},
    )

    assert result.name == "file.txt"
    assert result.parent.name == "app"


def test_use_root_false_absolute():
    absolute = Path.cwd() / "test_dir"

    definition = PathDefinition(str(absolute), use_root=False)

    result = definition.resolve(Path("/ignored"))

    assert result == absolute


def test_use_root_false_invalid_relative():
    with pytest.raises(InvalidPathDefinitionError):
        PathDefinition("relative/path", use_root=False)


def test_resolve_without_placeholders():
    definition = PathDefinition("logs")

    root = Path("/tmp")

    result = definition.resolve(root)

    assert str(result).endswith("logs")
