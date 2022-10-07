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
import os
import pkgutil
from typing import List, Tuple


class BaseMayaConfig(object):
    """Base class for all config classes.

    If you implement your own config class you need to populate `self._command_data`.

    """

    def __init__(self, modules: List[Tuple[str, str]]):
        """Construct class and populate modules.

        Args:
            modules: List of maya modules to look for maya commands.

        """
        self.modules = modules
        self._command_data = {}

    def get_flags(self, command_name: str) -> dict:
        """Try to get command flags from command name.

        Args:
            command_name: Maya command name to query for flags.

        Returns:
            Flags dict for command.

        """
        return self._command_data.get(command_name, {})


class MayaArgsConfig(BaseMayaConfig):
    """Class to manage maya flags configuration."""

    def __init__(self, config_version: str = "2022", modules: List[Tuple[str, str]] = (("maya", "cmds"),)):
        """Construct class and load config.

        Args:
            config_version: Configuration name.
            modules: List of maya modules to look for maya commands.

        """
        super().__init__(modules)
        self._command_data = json.loads(pkgutil.get_data("mayaff", f"maya_configs/{config_version}.json"))


class MayaFileArgsConfig(BaseMayaConfig):
    """Class to manage maya flags configuration."""

    def __init__(self, file_path: str, modules: List[Tuple[str, str]] = (("maya", "cmds"),)):
        """Construct class and load config.

        Args:
            file_path: Config file path to load.
            modules: List of maya modules to look for maya commands.

        """
        super().__init__(modules)
        if not os.path.exists(file_path):
            raise OSError(f'Config file "{file_path}" does not exist')

        with open(file_path) as f:
            self._command_data = json.load(f)
