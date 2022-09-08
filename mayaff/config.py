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

import json
import pkgutil
from typing import List, Tuple


class MayaArgsConfig(object):
    """Class to manage maya flags configuration."""

    def __init__(self, config_version: str = "2018", modules: List[Tuple[str, str]] = tuple(("maya", "cmds"))):
        """Construct class and load config.

        Args:
            config_version: Configuration name.
            modules: List of maya modules to look for maya commands.

        """
        super().__init__()
        self._command_data = json.loads(pkgutil.get_data("mayaff", f"maya_configs/{config_version}.json"))
        self.modules = modules

    def get_flags(self, command_name: str) -> dict:
        """Try to get command flags from command name.

        Args:
            command_name: Maya command name to query for flags.

        Returns:
            Flags dict for command.

        """
        return self._command_data.get(command_name, {})
