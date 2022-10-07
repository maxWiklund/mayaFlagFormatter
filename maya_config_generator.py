#!/usr/bin/env mayapy
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

import argparse
import inspect
import json
import keyword
import os
import re

from maya import cmds, mel, standalone

_RE_MAYA_COMMAND_FLAGS = re.compile(r"-(?P<short>\w+) -(?P<long>\w+)")


def generate(file_path: str) -> None:
    """Generate json file with all maya commands flags as key values.

    Args:
        file_path (str): File path to write json config to.

    """
    all_commands = {}
    file_path = file_path if file_path.endswith(".json") else f"{file_path}.json"

    for command, data in inspect.getmembers(cmds):
        try:
            text = mel.eval("help {}".format(command))

            arg_dict = {}
            for keys in _RE_MAYA_COMMAND_FLAGS.finditer(text):
                if keyword.iskeyword(keys.group("long")) or keyword.iskeyword(keys.group("short")):
                    continue

                arg_dict[keys.group("short")] = keys.group("long")

            if arg_dict:
                all_commands[command] = arg_dict
        except Exception:
            print("Error: {}".format(command))

    with open(file_path, "w") as outfile:
        json.dump(all_commands, outfile, indent=4)


def run() -> None:
    """Run as mayapy and generate json config file."""
    parser = argparse.ArgumentParser()
    parser.add_argument("output", default="", help="File path to export json file to.")
    args = parser.parse_args()
    standalone.initialize()
    try:
        file_path = os.path.realpath(args.output)
        generate(file_path)
    finally:
        standalone.uninitialize()


if __name__ == "__main__":
    run()
