from typing import (
    str,
    List,
    Dict,
)
import logging
from pytube import YouTube

# Create FileTree Class
class FileTree:

    def __init__(self) -> None:
        self.root = "./videos/"
        self.logger = logging.getLogger(__name__)

    def from_json(self, json_file: str) -> None:
        '''
        Load a json file and create a file tree
        '''
        