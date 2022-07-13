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

import tokenize
from dataclasses import dataclass
from typing import List, Optional


@dataclass()
class FlagArg:
    """Class representing Maya command flag."""

    short_name: str
    long_name: str
    lineno: int
    start: int
    end: int


@dataclass()
class FlagKwargs:
    """Class representing maya command with flags to reformat."""

    command_name: str  # Maya command name.
    flag_tokens: List[Optional[FlagArg]]


def create_flag_arg(token: tokenize.TokenInfo, long_name: str) -> FlagArg:
    """Convenience function to create FlagArgs instances.

    Args:
        token: Token with flag arg.
        long_name: Long flag arg name.

    Returns:
        Class representing flag arg to format.

    """
    return FlagArg(
        short_name=token.string,
        long_name=long_name,
        lineno=token.start[0] - 1,  # Converting line start from 1 to 0.
        start=token.start[1],
        end=token.end[1],
    )
