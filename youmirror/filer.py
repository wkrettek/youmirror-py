"""
This module manages the filetree
----
This is the second most important module in the project, it must be able to
generate the paths and filenames that make up the project with the given options
and resolve any naming conflicts. Thankfully, we can do most of our work with just
pathlib and some crafty organization
----
This is what the filetree looks like:
   Root
    | -- channels
            | -- channel name
                    | -- single name
                            | -- files
    | -- playlists
            | -- playlist name
                    | -- single name
                            | -- files
    | -- singles
            | -- single name
                    | -- files
----
"""

from pathlib import Path
from pytube.helpers import safe_filename
import logging

valid_file_types = {"video", "caption", "audio", "thumbnail"}  # Valid file types


def file_exists(filepath: Path) -> bool:
    """
    Checks if the config exists in the current working directory
    """
    try:
        return filepath.is_file()  # Check if the file exists
    except Exception as e:
        logging.info(f"Could not check file {filepath} due to {e}")
        return False


def create_file(filepath: Path) -> None:
    """
    Creates a file given a path and filename
    """
    try:
        if not filepath.is_file():
            filepath.open(mode="w")
    except Exception as e:
        print(e)


def create_path(path: Path) -> None:
    """
    Creates the path
    """
    try:
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)


def calculate_path(yt_string: str, parent_name: str, single_name) -> str:
    """
    Calculates
    formula = /yt_strings/parent_name/single_name
    This is gonna be refactored cause I'm not using it the intended way in get_keys()
    """
    valid_yt_strings = {"channel", "playlist", "single"}  # Valid yt strings
    parent_name = safe_filename(parent_name).replace(
        " ", "_"
    )  # Sanitize the parent name (using pytube)
    single_name = safe_filename(single_name).replace(
        " ", "_"
    )  # Sanitize the single name (using pytube)
    if yt_string in valid_yt_strings:  # Check the yt_string is valid
        yt_string = yt_string + "s"  # Make plural for formatting reasons
        path = (
            Path(yt_string) / Path(parent_name) / Path(single_name)
        )  # Build the filepath
        return str(path)
    else:
        logging.error(f"Invalid yt_string {yt_string} passed")


def calculate_filename(file_type: str, yt_name: str) -> str:
    """
    Calculates the filename from the given database settings and returns a string
    """

    file_type_to_extension = {
        "video": "mp4",
        "caption": "srt",
        "audio": "mp4",
        "thumbnail": "jpg",
    }
    if file_type in valid_file_types:  # Verify the file type is valid
        filename = safe_filename(yt_name).replace(" ", "_")  # Sanitize the filename
        extension = file_type_to_extension[
            file_type
        ]  # Convert the file type to an extension
        if file_type == "audio":  # If the file type is audio
            filename = f"{filename}_audio"  # Append "_audio" to the end of the filename
        filename = f"{filename}.{extension}"  # Add the name and extension together
        return filename
    else:
        logging.error(f"Invalid file type {file_type} passed")


def calculate_filepath(
    file_type: str,
    yt_string: str,
    parent_name: str,
    single_name: str,
) -> str:
    """
    Calculates what filepaths apply to a given
    """
    path = calculate_path(yt_string, parent_name, single_name)  # Get the path
    filename = calculate_filename(file_type, single_name)  # Get the filename
    filepath = Path(path) / Path(filename)  # Add them together
    return str(filepath)


# TODO
def resolve_collision(path: str, filetree: dict, yt_id: str) -> str:
    """
    Appends the yt_id if the path already exists
    """
    if path in filetree:  # If the path already exists
        logging.debug(f"Path {path} already exists")
        suffix = str(Path(path).suffix)  # Get the suffix of the path
        path = str(Path(path).with_suffix(""))  # Remove the suffix
        path = f"{path}_{yt_id}{suffix}"  # Append "_ym{yt_id}" to the end of the name, reattach suffix
    return path


def verify_installation(filepath: Path) -> bool:
    """
    Take a database entry and verify that it is fully installed
    """
    logging.info(f"Checking if file {filepath}")
    if filepath.is_file():
        logging.info(f"File {filepath} is installed")
        return True
    else:
        logging.info(f"File {filepath} is not installed")
    return False


def get_files(path: str, yt_name: str, options: dict) -> dict:
    """
    Returns a dict of filenames we want to download
    files = {filepath: {type: file_type, language: language}, filepath: {type: file_type, language: language}}
    """
    to_download = {  # Returns true/false if we want to download the video
        "video": options["dl_video"],
        "audio": options["dl_audio"],
        "caption": options["dl_captions"],
        "thumbnail": options["dl_thumbnail"],
    }
    files = dict()
    for file_type in to_download:
        if to_download[file_type]:  # Check the boolean value matching the file_type
            if file_type == "caption":
                for language in options[
                    "captions"
                ]:  # We can download multiple caption types
                    filename = calculate_filename(
                        file_type, f"{yt_name}_{language}"
                    )  # Add f'_{caption_type}'
                    filepath = str(Path(path) / filename)
                    files[filepath] = {
                        "type": file_type,
                        "language": language,
                    }  # Add to files
            else:
                filename = calculate_filename(
                    file_type, yt_name
                )  # Calculate the filename
                filepath = str(Path(path) / filename)
                files[filepath] = {"type": file_type}  # Add to files

    return files
