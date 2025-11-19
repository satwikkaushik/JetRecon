"""Utility functions for file operations"""

import os
from utils.errors import NotFoundError


def assert_file_exists(file_path: str) -> None:
    """Asserts that a file exists at the given path"""

    if not os.path.isfile(file_path):
        raise NotFoundError(f"The file at {file_path} does not exist.")


def get_file_size(path: str) -> int:
    """Returns the size of the file at the given path in bytes"""

    assert_file_exists(path)
    return os.path.getsize(path)
