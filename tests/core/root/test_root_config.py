from pathlib import Path

import pytest

from infra_core.core.root.exceptions import (
    InvalidRootMarkerError,
    InvalidRootStartPathError,
    RootMarkerNotFoundError,
)
from infra_core.core.root.root_config import RootConfig


def test_default_markers_are_populated():
    config = RootConfig()

    assert ".git" in config.markers


def test_add_marker_returns_new_config():
    config = RootConfig()

    updated = config.addMarker(".env")

    assert ".env" in updated.markers
    assert ".env" not in config.markers


def test_add_invalid_marker_raises():
    config = RootConfig()

    with pytest.raises(InvalidRootMarkerError):
        config.addMarker("")


def test_remove_missing_marker_raises():
    config = RootConfig()

    with pytest.raises(RootMarkerNotFoundError):
        config.removeMarker(".unknown")


def test_with_start_path_normalizes_file_to_parent(tmp_path: Path):
    config_file = tmp_path / "app.py"
    config_file.touch()

    config = RootConfig().withStartPath(config_file)

    assert config.start_path == tmp_path


def test_with_invalid_start_path_raises():
    with pytest.raises(InvalidRootStartPathError):
        RootConfig().withStartPath("")
