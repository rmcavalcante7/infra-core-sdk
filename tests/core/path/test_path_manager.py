# ============================================================
# Dependencies:
# - pytest
# - pathlib
# ============================================================

from pathlib import Path
import pytest

from infra_core.core.path.path_definition import PathDefinition
from infra_core.core.path.path_config_provider import PathConfigProvider
from infra_core.core.path.path_manager import PathManager
from infra_core.core.path.exceptions import PathNotFoundError

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture(autouse=True)
def reset_config():
    """
    Reset PathConfigProvider before each test.
    """
    from infra_core.core.path.path_config import PathConfig

    PathConfigProvider.set(PathConfig())
    yield
    PathConfigProvider.set(PathConfig())


@pytest.fixture
def manager(tmp_path, monkeypatch):
    """
    Provides PathManager with isolated root.

    :param tmp_path:
    :param monkeypatch:

    :return: PathManager
    """
    from infra_core.core.root.root_resolver import RootResolver

    def mock_resolve(self):
        return tmp_path

    monkeypatch.setattr(RootResolver, "resolve", mock_resolve)

    return PathManager()


# ============================================================
# Tests
# ============================================================


def test_root_resolution(manager: PathManager):
    root = manager.getRoot()

    assert isinstance(root, Path)
    assert root.exists()


def test_create_directory(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("logs", PathDefinition("logs/{name}"))
    PathConfigProvider.set(config)

    path = manager.createPath("logs", name="app")

    assert path.exists()
    assert path.is_dir()


def test_create_file(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("file", PathDefinition("logs/{dir}/{name}"))
    PathConfigProvider.set(config)

    path = manager.createPath(
        "file",
        variables={"dir": "app", "name": "file.txt"},
        is_file=True,
    )

    assert path.exists()
    assert path.is_file()


def test_ensure_path_exists(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("logs", PathDefinition("logs/{name}"))
    PathConfigProvider.set(config)

    path = manager.ensurePathExists("logs", name="app")

    assert path.exists()


def test_delete_file(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("file", PathDefinition("logs/{dir}/{name}"))
    PathConfigProvider.set(config)

    path = manager.createPath(
        "file",
        variables={"dir": "app", "name": "file.txt"},
        is_file=True,
    )

    manager.deleteResource(
        "file",
        variables={"dir": "app", "name": "file.txt"},
    )

    assert not path.exists()


def test_delete_directory(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("logs", PathDefinition("logs/{name}"))
    PathConfigProvider.set(config)

    path = manager.createPath("logs", name="app")

    manager.deleteResource("logs", name="app")

    assert not path.exists()


def test_missing_path_raises(manager: PathManager):
    with pytest.raises(PathNotFoundError):
        manager.getPath("invalid")


def test_remove_from_config(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("logs", PathDefinition("logs"))
    PathConfigProvider.set(config)

    manager.removeFromConfig("logs")

    with pytest.raises(PathNotFoundError):
        manager.getPath("logs")


def test_variables_resolution(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("multi", PathDefinition("logs/{dir}/{name}"))
    PathConfigProvider.set(config)

    path = manager.getPath(
        "multi",
        variables={"dir": "app", "name": "file.txt"},
    )

    assert path.name == "file.txt"
    assert path.parent.name == "app"


def test_backward_compatibility(manager: PathManager):
    config = PathConfigProvider.get()
    config = config.addPath("logs", PathDefinition("logs/{name}"))
    PathConfigProvider.set(config)

    path = manager.getPath("logs", name="app")

    assert path.name == "app"


def test_use_root_false_absolute():
    config = PathConfigProvider.get()

    absolute_path = Path.cwd()

    config = config.addPath(
        "external", PathDefinition(str(absolute_path), use_root=False)
    )

    PathConfigProvider.set(config)

    manager = PathManager()

    path = manager.getPath("external")

    assert path == absolute_path
