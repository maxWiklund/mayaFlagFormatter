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

from typing import List

from mayaff import flags


def reformat(source_code: str, command_flags: List[flags.FlagKwargs]) -> str:
    """Reformat source code.

    Args:
        source_code: Source code to reformat.
        command_flags: Flags to format.

    Returns:
        str: Formatted source code.

    """

    lines = source_code.split("\n")

    def _format(command_flag: flags.FlagKwargs) -> None:
        for node in reversed(command_flag.flag_tokens):
            if isinstance(node, flags.FlagKwargs):
                _format(node)
            else:
                line = lines[node.lineno]
                lines[node.lineno] = line[: node.start] + node.long_name + line[node.end :]

    for flag in reversed(command_flags):
        _format(flag)

    return "\n".join(lines)
