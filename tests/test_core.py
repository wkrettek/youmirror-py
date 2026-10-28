from pathlib import Path
from unittest import mock

import pytest

from youmirror.configurer import load_config, save_config, set_yt
from youmirror.core import YouMirror, folder_name, format_sort, source_dir, ydl_args


def test_folder_name_matches_old_layout():
    assert folder_name("The Always Sunny Podcast") == "The_Always_Sunny_Podcast"
    assert folder_name("Accursed Farms") == "Accursed_Farms"


def test_source_dir():
    assert source_dir("channel", "The Minute Hour") == "channels/The_Minute_Hour"
    assert source_dir("playlist", "Memes") == "playlists/Memes"
    assert source_dir("single", "anything") == "singles"


def test_format_sort():
    assert format_sort("best") == "res,vcodec:av01"
    assert format_sort("1080p") == "res:1080,vcodec:av01"
    with pytest.raises(ValueError):
        format_sort("high")


def test_ydl_args_uses_mirror_paths(tmp_path: Path):
    args = ydl_args(tmp_path, "channel", {"name": "Settled"}, dry_run=True)
    output = args[args.index("--output") + 1]
    assert output.startswith(str(tmp_path / "channels/Settled"))
    assert args[args.index("--download-archive") + 1] == str(
        tmp_path / ".youmirror/archive.txt"
    )
    assert "--simulate" in args


def test_bad_resolution_is_an_error_not_a_crash(tmp_path: Path):
    mirror = YouMirror(root=str(tmp_path))
    mirror.new()
    with mock.patch(
        "youmirror.core.identify", return_value=("channel", "A")
    ) as identify:
        assert not mirror.add("https://www.youtube.com/@a", "high", None, True)
    identify.assert_not_called()

    config = load_config(mirror.config_path)
    set_yt("playlist", "https://a", config, {"name": "A", "resolution": "high"})
    set_yt("playlist", "https://b", config, {"name": "B"})
    save_config(mirror.config_path, config)
    with mock.patch("youmirror.core.run_ydl", return_value=0) as run_ydl:
        mirror.sync(None, dry_run=True)
    assert [call.args[1] for call in run_ydl.call_args_list] == ["https://b"]
