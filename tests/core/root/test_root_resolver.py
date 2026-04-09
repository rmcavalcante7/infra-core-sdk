# ============================================================
# Dependencies:
# - pytest
# - pathlib
# ============================================================

from pathlib import Path
import pytest

from infra_core.core.root.root_config import RootConfig
from infra_core.core.root.root_config_provider import RootConfigProvider
from infra_core.core.root.root_resolver import RootResolver
from infra_core.core.root.exceptions import RootResolutionError

# ============================================================
# Helpers
# ============================================================


def create_fake_project(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()

    (root / ".git").mkdir()

    return root


@pytest.fixture(autouse=True)
def reset_root_provider():
    RootConfigProvider.reset()
    yield
    RootConfigProvider.reset()


# ============================================================
# Tests
# ============================================================


def test_resolve_with_git_marker(tmp_path, monkeypatch):
    root = create_fake_project(tmp_path)

    subdir = root / "a" / "b"
    subdir.mkdir(parents=True)

    monkeypatch.chdir(subdir)

    resolver = RootResolver()

    resolved = resolver.resolve()

    assert resolved == root


def test_resolve_with_pyproject_marker(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()

    (root / "pyproject.toml").touch()

    subdir = root / "x" / "y"
    subdir.mkdir(parents=True)

    monkeypatch.chdir(subdir)

    resolver = RootResolver()

    resolved = resolver.resolve()

    assert resolved == root


def test_resolve_from_root(tmp_path, monkeypatch):
    root = create_fake_project(tmp_path)

    monkeypatch.chdir(root)

    resolver = RootResolver()

    resolved = resolver.resolve()

    assert resolved == root


def test_resolve_nested_structure(tmp_path, monkeypatch):
    root = create_fake_project(tmp_path)

    subdir = root / "deep" / "nested" / "dir"
    subdir.mkdir(parents=True)

    monkeypatch.chdir(subdir)

    resolver = RootResolver()

    resolved = resolver.resolve()

    assert resolved == root


def test_resolve_no_marker_raises(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()

    subdir = root / "nested"
    subdir.mkdir()

    monkeypatch.chdir(subdir)

    resolver = RootResolver()

    with pytest.raises(RootResolutionError):
        resolver.resolve()


def test_resolve_caching(tmp_path, monkeypatch):
    root = create_fake_project(tmp_path)

    subdir = root / "a"
    subdir.mkdir()

    monkeypatch.chdir(subdir)

    resolver = RootResolver()

    first = resolver.resolve()
    second = resolver.resolve()

    assert first == second


def test_resolve_with_configured_start_path(tmp_path, monkeypatch):
    root = create_fake_project(tmp_path)
    subdir = root / "service" / "api"
    subdir.mkdir(parents=True)

    monkeypatch.chdir(tmp_path.parent)
    RootConfigProvider.set(RootConfig(markers=(".git",), start_path=subdir))

    resolver = RootResolver()

    assert resolver.resolve() == root


def test_resolve_uses_caller_path_when_cwd_is_outside_project(tmp_path, monkeypatch):
    root = create_fake_project(tmp_path)
    app_dir = root / "src_app"
    app_dir.mkdir()

    external_cwd = tmp_path / "outside"
    external_cwd.mkdir()

    monkeypatch.chdir(external_cwd)
    monkeypatch.setattr(RootResolver, "_shouldUseCallerFallback", lambda self: True)
    monkeypatch.setattr(RootResolver, "_getCallerPath", lambda self: app_dir)

    resolver = RootResolver()

    assert resolver.resolve() == root
