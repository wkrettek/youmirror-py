"""
This module manages the config
I decided on using toml over json because it's easier to read and edit.
tomlkit keeps comments and formatting when the config is saved back.
"""

import logging
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import tomlkit
from tomlkit import TOMLDocument

from youmirror.template import template

logger = logging.getLogger(__name__)
config_file = "youmirror.toml"  # This is the name for the config file to be used
valid_yt = ("channel", "playlist", "single")  # Valid source types for the config
default_resolution = "best"


def load_config(config_path: Path) -> TOMLDocument | None:
    """
    Loads the config file, or returns None if it is missing or invalid
    """
    if not config_path.is_file():
        logger.error(f"Config file {config_path} does not exist")
        return None
    try:
        with config_path.open("r") as f:
            return tomlkit.load(f)
    except tomlkit.exceptions.ParseError as e:
        logger.error(f"Could not parse config file {config_path}: {e}")
        return None


def save_config(config_path: Path, config: TOMLDocument) -> None:
    """
    Writes the config to the config file
    """
    config_path.write_text(tomlkit.dumps(config))


def new_config(config_path: Path, name: str) -> None:
    """
    Creates a new config file from the template
    """
    config = tomlkit.document()
    config.update(deepcopy(template))
    config["youmirror"]["name"] = name
    config["youmirror"]["created_at"] = datetime.now().strftime("%Y-%m-%d")
    save_config(config_path, config)


def find_yt(url: str, config: TOMLDocument) -> str | None:
    """
    Returns the section ("channel", "playlist", "single") that tracks the url
    """
    for yt_string in valid_yt:
        if url in config.get(yt_string, {}):
            return yt_string
    return None


def get_sources(config: TOMLDocument) -> list[tuple[str, str, dict]]:
    """
    Returns (yt_string, url, settings) for every tracked source
    """
    sources: list[tuple[str, str, dict]] = []
    for yt_string in valid_yt:
        for url, settings in config.get(yt_string, {}).items():
            sources.append((yt_string, url, settings))
    return sources


def set_yt(yt_string: str, url: str, config: TOMLDocument, settings: dict) -> None:
    """
    Sets the settings for the url in its section
    """
    if yt_string not in config:
        config[yt_string] = tomlkit.table()
    config[yt_string][url] = settings


def remove_yt(yt_string: str, url: str, config: TOMLDocument) -> None:
    """
    Removes the url from its section
    """
    if url in config.get(yt_string, {}):
        del config[yt_string][url]
