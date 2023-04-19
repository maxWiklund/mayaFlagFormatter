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

import io
import os

from mayaff import file_resources, output, pyparser, reformatter
from mayaff.config import MayaArgsConfig


def format_file(
    file_name: str,
    config: MayaArgsConfig = None,
    quiet: bool = False,
    check_only: bool = False,
    print_diff: bool = False,
) -> bool:
    """Reformat file.

    Args:
        file_name: File path to file to format.
        config (optional) Maya commands config.
        quiet: If True don't print messages.
        check_only: Don't write changes only return status.
        print_diff: If True only print diff.

    Raises:
        SyntaxError: If source code is invalid.

    Returns:
        bool: True if changes found else False.

    """
    config = config if config else MayaArgsConfig()
    source_code, encoding = file_resources.read_file(file_name)

    parser = pyparser.MayaFlagsParser(config)
    flags = parser.parse_string(source_code, file_name)

    if not flags or check_only:
        return bool(flags)

    reformatted_source = reformatter.reformat(source_code, flags)
    if print_diff:
        print(output.diff(source_code, reformatted_source, file_name))
        return True

    with io.open(file_name, mode="w", encoding=encoding, newline="") as f:
        f.write(reformatted_source)

    if not quiet:
        print(f"reformatted {os.path.relpath(file_name)}")

    return True


def format_string(source_code: str, config: MayaArgsConfig = None) -> str:
    """Reformat source code.

    Args:
        source_code: Code to format.
        config (optional) Maya commands config.

    Returns:
        Reformatted code.

    """
    config = config if config else MayaArgsConfig()
    parser = pyparser.MayaFlagsParser(config)
    flags = parser.parse_string(source_code)
    return reformatter.reformat(source_code, flags) if flags else source_code
