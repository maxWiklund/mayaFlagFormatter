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
import multiprocessing
import re
import sys
import os
from concurrent import futures
from typing import List, Tuple

from mayaff import file_resources, mayaff_api, output
from mayaff.config import MayaArgsConfig, MayaFileArgsConfig, CONFIG_OPTIONS, LATEST_CONFIG

__version__ = "1.1.0"
_DESCRIPTION = "Command line tool to find and replace short maya flags."


def config_exists(parser: argparse.ArgumentParser, file_path: str) -> None:
    """Check if config file exists on disk."""
    if not os.path.exists(file_path):
        parser.error(f"Config file {file_path} does not exist!")


def set_up_argparser() -> argparse.Namespace:
    """Configure argparser."""
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument("-v", "--version", action="version", version="%(prog)s {}".format(__version__))
    parser.add_argument("source", nargs="+", help="Directory or files you want to format.")

    config_group = parser.add_mutually_exclusive_group()

    config_group.add_argument(
        "-t",
        "--target-version",
        default=LATEST_CONFIG,
        choices=CONFIG_OPTIONS,
        help="Target Maya version to use when formatting flags.",
    )

    config_group.add_argument(
        "--config", help="Custom maya config file. If you want to provide a custom config file different to the target options."
    )

    parser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Don't write to files. Just return the return code.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Don't write the files back, just output a diff for each file to stdout.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Output nothing to stdout and set return value.",
    )
    parser.add_argument(
        "--exclude",
        default=r"\..+",
        help="A regular expression for file names to exclude.",
    )
    parser.add_argument("--exclude-files", nargs="+", default=[], help="Exclude files. Separate files with space.")
    parser.add_argument(
        "--modules",
        default="maya:cmds,pymel:core",
        help="Maya modules to use for import. Examples: --modules 'maya:cmds,pymel:core'",
    )
    parser.add_argument("--single-thread", action="store_true", default=False, help="Only execute mayaff on single thread.")
    return parser.parse_args()


def _main() -> int:
    """Run command line app with return code."""
    args = set_up_argparser()
    modules = [tuple(m.split(":")) for m in args.modules.split(",")]

    _config = MayaFileArgsConfig(args.config, modules) if args.config else MayaArgsConfig(args.target_version, modules)
    try:
        exclude_re = re.compile(args.exclude)
    except re.error:
        raise UserWarning("Invalid exclude regular expression.")

    files = file_resources.find_python_files(args.source, args.exclude_files, exclude_pattern=exclude_re)
    if not files:
        raise UserWarning("No input files found.")

    files_changed, failed_files = format_files(files, _config, quiet=args.quiet, check_only=args.check, print_diff=args.diff)
    if not args.quiet:
        msg = []
        if files_changed:
            plural = "s" if files_changed > 1 else ""
            msg.append(f"{files_changed} file{plural} reformatted")
        if len(files) != files_changed + failed_files:
            msg.append(f"{len(files) - files_changed} files left unchanged.")

        if failed_files:
            plural = "s" if failed_files > 1 else ""
            output.print_failed(f"{failed_files} file{plural} failed to reformat.")
            return 1

        print(", ".join(msg))
        print("Done ✨")

    return 1 if files_changed and (args.diff or args.check) else 0


def format_files(
    file_paths: List[str],
    config: MayaArgsConfig,
    quiet: bool = False,
    check_only: bool = False,
    print_diff: bool = False,
    single_thread: bool = False,
) -> Tuple[int, int]:
    """Format files

    Args:
        file_paths: Python file paths to format.
        config: Config class to use for parsing.
        quiet: If True don't print anything.
        check_only: If True don't write result back to file.
        print_diff: If True only print diff and don't write to file.
        single_thread: If True only execute process on one thread.

    Returns:
        tuple: (Diff found, Number of files updated).

    """
    cpu = 1 if single_thread else multiprocessing.cpu_count()
    number_of_workers = min(cpu, len(file_paths))
    with futures.ProcessPoolExecutor(number_of_workers) as executor:
        workers = [
            executor.submit(
                _format_file,
                file_name=file_name,
                config=config,
                quiet=quiet,
                check_only=check_only,
                print_diff=print_diff,
            )
            for file_name in file_paths
        ]

        reformatted_files = 0
        failed_files = 0
        for future in futures.as_completed(workers):
            changed, failed = future.result()
            reformatted_files += changed
            failed_files += failed

    return reformatted_files, failed_files


def _format_file(
    file_name: str,
    config: MayaArgsConfig = None,
    quiet: bool = False,
    check_only: bool = False,
    print_diff: bool = False,
) -> Tuple[int, int]:
    """Reformat file.

    Args:
        file_name: File path to file to format.
        config (optional) Maya commands config.
        quiet: If True don't print messages.
        check_only: Don't write changes only return status.
        print_diff: If True only print diff.

    Returns:
        (File changed, Failed).

    """
    try:
        result = mayaff_api.format_file(
            file_name=file_name, config=config, quiet=quiet, check_only=check_only, print_diff=print_diff
        )
        return int(result), 0
    except Exception as e:
        output.print_failed(str(e))
        if not quiet:
            output.print_failed(f"Failed to reformat {file_name}.")
        return 0, 1


def run() -> None:
    """Start app."""
    try:
        sys.exit(_main())
    except Exception as e:
        output.print_failed(e)
        sys.exit(1)
