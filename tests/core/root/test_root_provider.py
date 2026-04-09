from pathlib import Path

from infra_core.core.root.root_config import RootConfig
from infra_core.core.root.root_config_provider import RootConfigProvider


def test_get_returns_default_config():
    RootConfigProvider.reset()

    config = RootConfigProvider.get()

    assert isinstance(config, RootConfig)


def test_set_persists_config(tmp_path: Path):
    config = RootConfig().withStartPath(tmp_path)

    RootConfigProvider.set(config)

    assert RootConfigProvider.get() == config


def test_reset_restores_default_config(tmp_path: Path):
    RootConfigProvider.set(RootConfig().withStartPath(tmp_path))

    RootConfigProvider.reset()

    assert RootConfigProvider.get().start_path is None
