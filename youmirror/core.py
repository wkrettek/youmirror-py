"""
This is the core module
------
youmirror.toml holds what the mirror should contain. yt-dlp does the work, and
its download archive (.youmirror/archive.txt) records what is already downloaded.
"""

import logging
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yt_dlp
from yt_dlp.utils import sanitize_filename

import youmirror.configurer as configurer

logger = logging.getLogger(__name__)
state_dir = ".youmirror"  # Holds files that youmirror manages
archive_file = "archive.txt"  # yt-dlp download archive
video_template = "%(title)s [%(id)s]"  # Folder and file name for each video


def folder_name(name: str) -> str:
    """
    Turns a source name into a folder name, "The Minute Hour" -> "The_Minute_Hour"
    """
    return re.sub(r"\s+", "_", sanitize_filename(name).strip())


def source_dir(yt_string: str, name: str) -> str:
    """
    Gets the folder for a source, relative to the mirror root
    """
    if yt_string == "single":
        return "singles"
    return f"{yt_string}s/{folder_name(name)}"


def format_sort(resolution: str) -> str:
    """
    Turns a resolution setting ("best", "1080p") into a yt-dlp format sort that prefers AV1
    """
    if resolution == "best":
        return "res,vcodec:av01"
    height = resolution.removesuffix("p")
    if not height.isdigit():
        raise ValueError(f"Invalid resolution '{resolution}', use 'best' or '<N>p'")
    return f"res:{height},vcodec:av01"


def ydl_args(root: Path, yt_string: str, settings: dict, dry_run: bool) -> list[str]:
    """
    Builds the yt-dlp command line arguments for one source
    """
    resolution = settings.get("resolution", configurer.default_resolution)
    folder = root / source_dir(yt_string, settings.get("name", ""))
    args = [
        "--format", "bv*+ba/b",
        "--format-sort", format_sort(resolution),
        "--merge-output-format", "mkv",
        "--output", str(folder / video_template / f"{video_template}.%(ext)s"),
        # Playlist and channel metadata go beside the video folders, not in one
        "--output", f"pl_infojson:{folder / video_template}.%(ext)s",
        "--output", f"pl_thumbnail:{folder / video_template}.%(ext)s",
        "--download-archive", str(root / state_dir / archive_file),
        "--write-subs", "--write-auto-subs", "--sub-langs", "en", "--sub-format", "vtt",
        "--embed-subs",
        "--write-thumbnail", "--convert-thumbnails", "jpg", "--embed-thumbnail",
        "--embed-metadata", "--embed-chapters",
        "--write-info-json",
        "--ignore-errors",
    ]  # fmt: skip
    if not sys.stderr.isatty():
        args.append("--no-progress")  # Progress bars flood the journal under systemd
    if dry_run:
        args.append("--simulate")
    return args


def run_ydl(args: list[str], url: str) -> int:
    """
    Runs yt-dlp on the url and returns its exit code (0 means every video succeeded)
    """
    ydl_opts = yt_dlp.parse_options(args).ydl_opts
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.download([url])


def identify(url: str) -> tuple[str, str] | None:
    """
    Asks yt-dlp what the url is and returns (yt_string, name)
    """
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Could not read url '{url}': {e}")
        return None
    if info.get("_type") != "playlist":
        return "single", info.get("title") or info["id"]
    if info.get("channel_id") and "list=" not in info.get("webpage_url", ""):
        return "channel", info.get("channel") or info.get("title") or info["id"]
    return "playlist", info.get("title") or info["id"]


class YouMirror:
    """
    Main class for maintaining a youmirror
    """

    def __init__(self, root: str = ".") -> None:
        self.path: Path = Path(root)
        self.config_path: Path = self.path / configurer.config_file

    def new(self) -> None:
        """
        Create a new mirror in the root directory
        """
        if self.config_path.is_file():
            logger.info(f"Config file '{self.config_path}' already exists")
            return
        (self.path / state_dir).mkdir(parents=True, exist_ok=True)
        configurer.new_config(self.config_path, self.path.absolute().name)
        logger.info(f"Created new mirror at '{self.path}'")

    def add(
        self, url: str, resolution: str | None, name: str | None, no_dl: bool
    ) -> bool:
        """
        Adds the url to the mirror and downloads it unless no_dl is set
        """
        if not (config := configurer.load_config(self.config_path)):
            return False
        if configurer.find_yt(url, config):
            logger.error(f"url '{url}' already exists in the mirror")
            return False
        if resolution:
            try:
                format_sort(resolution)  # Fail early on a bad value
            except ValueError as e:
                logger.error(e)
                return False
        if not (identified := identify(url)):
            return False
        yt_string, found_name = identified
        settings = {
            "name": name or found_name,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }
        if resolution:
            settings["resolution"] = resolution
        configurer.set_yt(yt_string, url, config, settings)
        configurer.save_config(self.config_path, config)
        logger.info(f"Added {yt_string} '{settings['name']}' to the mirror")
        if no_dl:
            return True
        return self.sync(url, dry_run=False)

    def remove(self, url: str, delete: bool) -> bool:
        """
        Stops tracking the url, and deletes its folder if delete is set
        """
        if not (config := configurer.load_config(self.config_path)):
            return False
        if not (yt_string := configurer.find_yt(url, config)):
            logger.error(f"url '{url}' is not in the mirror")
            return False
        name = config[yt_string][url].get("name", "")
        configurer.remove_yt(yt_string, url, config)
        configurer.save_config(self.config_path, config)
        logger.info(f"Removed {yt_string} '{name}' from the mirror")
        if delete and yt_string != "single":
            folder = self.path / source_dir(yt_string, name)
            shutil.rmtree(folder, ignore_errors=True)
            logger.info(f"Deleted '{folder}'")
        elif delete:
            logger.warning(
                "Deleting singles is not supported yet, delete the folder by hand"
            )
        return True

    def sync(self, url: str | None, dry_run: bool) -> bool:
        """
        Downloads everything in the mirror (or just the url) that is not downloaded yet
        """
        if not (config := configurer.load_config(self.config_path)):
            return False
        sources = configurer.get_sources(config)
        if url:
            sources = [source for source in sources if source[1] == url]
            if not sources:
                logger.error(f"url '{url}' is not in the mirror")
                return False
        (self.path / state_dir).mkdir(exist_ok=True)
        for yt_string, source_url, settings in sources:
            logger.info(f"Syncing {yt_string} '{settings.get('name', source_url)}'")
            try:
                args = ydl_args(self.path, yt_string, settings, dry_run)
            except ValueError as e:
                logger.error(f"Skipping '{source_url}': {e}")
                continue
            # Private or removed videos fail every run, so failures are warnings
            if run_ydl(args, source_url) != 0:
                logger.warning(
                    f"Some videos failed for '{source_url}', will retry next sync"
                )
            elif not dry_run:
                settings["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                configurer.save_config(self.config_path, config)
        return True

    def show(self) -> bool:
        """
        Shows the sources in the mirror and how many videos each has on disk
        """
        if not (config := configurer.load_config(self.config_path)):
            return False
        logger.info(f"Mirror '{config['youmirror'].get('name', '')}' at '{self.path}'")
        for yt_string, url, settings in configurer.get_sources(config):
            folder = self.path / source_dir(yt_string, settings.get("name", ""))
            count = (
                sum(1 for entry in folder.iterdir() if entry.is_dir())
                if folder.is_dir()
                else 0
            )
            resolution = settings.get("resolution", configurer.default_resolution)
            logger.info(
                f"  {yt_string:8} {settings.get('name', ''):40} {resolution:>6} {count:5} videos  {url}"
            )
        return True
