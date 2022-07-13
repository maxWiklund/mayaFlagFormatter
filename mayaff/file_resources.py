# Copyright (C) 2022  Max Wiklund
#
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import tokenize
from typing import Generator, List, Tuple


def find_python_files(directorys_and_files: List[str], exclude_files: List[str], exclude_pattern: re.Pattern) -> List[str]:
    """Find files to format on disk.

    Args:
        directorys_or_files: List of directories and files to format.
        exclude_files: Local file paths to exclude.
        exclude_pattern: Regular expression of file pattern to exclude.

    Returns:
        Found file paths that where not excluded by exclude pattern.

    """
    exclude_files = [os.path.realpath(fn) for fn in exclude_files]
    found_paths = set()
    for path in directorys_and_files:
        if os.path.isdir(path):
            for file_path in _walk_directory_and_find_valid_files(os.path.realpath(path)):
                if exclude_pattern.match(file_path):
                    continue
                if file_path in exclude_files:
                    continue
                found_paths.add(file_path)
        else:
            if path.endswith(".py"):
                found_paths.add(os.path.realpath(path))

    return list(found_paths)


def _walk_directory_and_find_valid_files(root_directory: str) -> Generator:
    """Recursively traverse directory and try to find python files.

    Args:
        root_directory: Root directory to travers.

    Yields:
        File that ends with `.py`.

    """
    for root, _, files in os.walk(root_directory):
        for f in files:
            if not f.endswith(".py"):
                continue

            yield os.path.join(root, f)


def read_file(file_name: str) -> Tuple[str, str]:
    """Read file and get file content and encoding.

    Args:
        file_name: File path to read.

    Returns:
        File content and file encoding.

    """
    encoding = file_encoding(file_name)
    with open(file_name) as f:
        return f.read(), encoding


def file_encoding(file_name: str) -> str:
    """Read file encoding form file path.

    Args:
        file_name: File path to read encoding from.

    Returns:
        File encoding name.

    """
    with open(file_name, "rb") as fd:
        return tokenize.detect_encoding(fd.readline)[0]
