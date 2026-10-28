from pathlib import Path

from youmirror.configurer import (
    find_yt,
    get_sources,
    load_config,
    new_config,
    remove_yt,
    save_config,
    set_yt,
)


def test_new_config_round_trip(tmp_path: Path):
    config_path = tmp_path / "youmirror.toml"
    new_config(config_path, "mirror")
    config = load_config(config_path)
    assert config["youmirror"]["name"] == "mirror"

    url = "https://www.youtube.com/@suckerpinch"
    set_yt("channel", url, config, {"name": "suckerpinch", "resolution": "1080p"})
    save_config(config_path, config)

    config = load_config(config_path)
    assert find_yt(url, config) == "channel"
    assert get_sources(config) == [
        ("channel", url, {"name": "suckerpinch", "resolution": "1080p"})
    ]

    remove_yt("channel", url, config)
    assert find_yt(url, config) is None


def test_load_config_keeps_comments(tmp_path: Path):
    config_path = tmp_path / "youmirror.toml"
    config_path.write_text('# my mirror\n[youmirror]\nname = "m"\n')
    save_config(config_path, load_config(config_path))
    assert config_path.read_text().startswith("# my mirror")


def test_load_config_missing(tmp_path: Path):
    assert load_config(tmp_path / "youmirror.toml") is None
