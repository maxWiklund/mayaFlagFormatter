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


import difflib


def print_failed(msg: str) -> None:
    print(f"\033[31m{msg}\033[0m")


def diff(source_a: str, source_b: str, file_name: str) -> str:
    """Generate diff of source with color.

    Args:
        source_a: Source code.
        source_b: Format source code.
        file_name: File name of source code.

    Returns:
        Diff string with color.

    """
    a_lines = source_a.splitlines(keepends=True)
    b_lines = source_b.splitlines(keepends=True)
    lines = []
    for line in difflib.unified_diff(a_lines, b_lines, fromfile=file_name, tofile=file_name, n=5):
        if line.startswith("+++") or line.startswith("---"):
            line = "\033[1m" + line + "\033[0m"  # bold, reset
        elif line.startswith("@@"):
            line = "\033[36m" + line + "\033[0m"  # cyan, reset
        elif line.startswith("+"):
            line = "\033[32m" + line + "\033[0m"  # green, reset
        elif line.startswith("-"):
            line = "\033[31m" + line + "\033[0m"  # red, reset

        lines.append(line)

    return "".join(lines)
