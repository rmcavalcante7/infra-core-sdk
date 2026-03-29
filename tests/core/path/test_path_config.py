# ============================================================
# Dependencies:
# - pytest
# ============================================================

import pytest

from infra_core.core.path.path_definition import PathDefinition
from infra_core.core.path.path_config import PathConfig
from infra_core.core.path.exceptions import (
    PathNotFoundError,
    PathAlreadyExistsError,
)

# ============================================================
# Tests
# ============================================================


def test_add_path():
    config = PathConfig()

    new_config = config.addPath("logs", PathDefinition("logs"))

    assert "logs" in new_config.paths
    assert "logs" not in config.paths  # imutabilidade


def test_add_multiple_paths():
    config = PathConfig()

    config = config.addPath("logs", PathDefinition("logs"))
    config = config.addPath("data", PathDefinition("data"))

    assert "logs" in config.paths
    assert "data" in config.paths


def test_add_path_duplicate_raises():
    config = PathConfig()

    config = config.addPath("logs", PathDefinition("logs"))

    with pytest.raises(PathAlreadyExistsError):
        config.addPath("logs", PathDefinition("new_logs"))


def test_update_path():
    config = PathConfig()

    config = config.addPath("logs", PathDefinition("logs"))

    updated_config = config.updatePath("logs", PathDefinition("new_logs"))

    assert updated_config.paths["logs"].path == "new_logs"
    assert config.paths["logs"].path == "logs"  # imutável


def test_update_nonexistent_path():
    config = PathConfig()

    with pytest.raises(PathNotFoundError):
        config.updatePath("invalid", PathDefinition("logs"))


def test_remove_path():
    config = PathConfig()

    config = config.addPath("logs", PathDefinition("logs"))

    new_config = config.removePath("logs")

    assert "logs" not in new_config.paths
    assert "logs" in config.paths  # imutabilidade


def test_remove_nonexistent_path():
    config = PathConfig()

    with pytest.raises(PathNotFoundError):
        config.removePath("invalid")


def test_get_definition_via_dict():
    config = PathConfig()

    definition = PathDefinition("logs")

    config = config.addPath("logs", definition)

    result = config.paths["logs"]

    assert result == definition


def test_get_nonexistent_definition():
    config = PathConfig()

    with pytest.raises(KeyError):
        _ = config.paths["invalid"]


def test_config_is_immutable_chain():
    config = PathConfig()

    config2 = config.addPath("logs", PathDefinition("logs"))
    config3 = config2.updatePath("logs", PathDefinition("new_logs"))
    config4 = config3.removePath("logs")

    # Estado original
    assert "logs" not in config.paths

    # Após add
    assert "logs" in config2.paths
    assert config2.paths["logs"].path == "logs"

    # Após update
    assert config3.paths["logs"].path == "new_logs"

    # Após remove
    assert "logs" not in config4.paths
