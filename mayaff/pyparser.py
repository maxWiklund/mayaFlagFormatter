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

import ast
import io
import logging
import token
import tokenize
from typing import Callable, List

from mayaff import flags
from mayaff.config import MayaArgsConfig

LOG = logging.getLogger(__name__)


class Lexer(object):
    """Python lexer class with peek method."""

    def __init__(self, read_line: Callable):
        """Construct class and do nothing.

        Args:
            read_line: Read line function from `io.StringIO` or `open`.

        """
        super().__init__()
        self._tokens_generator = tokenize.generate_tokens(read_line)
        self._tokens_ahead = []
        self._token = None

    def token(self) -> tokenize.TokenInfo:
        """Current token."""
        return self._token

    def _next_token(self) -> tokenize.TokenInfo:
        """Get next token.

        Raises:
            StopIteration: If you reach end of file.

        Returns:
            Next token from source.

        """
        if self._tokens_ahead:
            return self._tokens_ahead.pop()
        return next(self._tokens_generator)

    def advance(self) -> None:
        """Consume next token."""
        self._token = self._next_token()

    def peek(self) -> tokenize.TokenInfo:
        """Look at next token.

        Raises:
            StopIteration: If you reach end of file.

        Returns:
            Next token from source without consuming it.

        """
        tok = self._next_token()
        self._tokens_ahead.append(tok)
        return tok


class MayaImportVisitor(ast.NodeVisitor):
    """Ast traversal class to find cmds import from maya."""

    def __init__(self, modules):
        """Construct class and do nothing."""
        super().__init__()
        self.maya_imports = []
        self.modules = modules

    def visit_Import(self, node: ast.Import) -> None:
        """Code to check if `maya.cmds` is imported.

        Args:
            node: Node to check if maya is imported.

        """
        for _import in node.names:
            for imp in self.modules:
                if _import.name == ".".join(imp):
                    self.maya_imports.append(_import.asname or _import.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Code to check if `maya.cmds` is imported.

        Args:
            node: Node to check if maya is imported.

        """
        for _import in node.names:
            for module, imp in self.modules:
                if node.module == module and _import.name == imp:
                    self.maya_imports.append(_import.asname or _import.name)


class MayaFlagsParser(object):
    """Parser class for parsing python `cmds` command flag names.

    The class implements a recursive descent parser for finding maya command flags.

    """

    def __init__(self, config: MayaArgsConfig):
        """Construct parser and do nothing.

        Args:
            config(MayaArgsConfig): Config class to use for parsing.

        """
        super().__init__()
        self._config = config
        self._found_maya_modules = []
        self._lexer: Lexer = None
        self._command_flags = []

    def parse_file(self, file_name: str) -> List[flags.FlagKwargs]:
        """Parse python file.

        Args:
            file_name: Path to file to parse.

        Returns:
            list: Found maya commands with flags information.

        """
        with open(file_name) as f:
            self._parse_maya_imports(f.read(), file_name)
            if not self._found_maya_modules:
                LOG.debug(f"No maya commands found in {file_name}")
                return []

            self._lexer = Lexer(f.readline)

        self._parse_stream()
        return self._command_flags

    def parse_string(self, source_code: str, file_name: str = "<unknown>") -> List[flags.FlagKwargs]:
        """Parse source code to maya flags.

        Args:
            source_code: Source code (python) with maya commands to find.
            file_name: File path to source.

        Returns:
            list: Found maya commands with flags information.

        """
        self._parse_maya_imports(source_code, file_name)
        if not self._found_maya_modules:
            LOG.debug(f"No maya commands found in source.")
            return []

        self._lexer = Lexer(io.StringIO(source_code).readline)
        self._parse_stream()
        return self._command_flags

    def _parse_stream(self) -> None:
        """Parse tokens."""
        while True:
            try:
                self._lexer.advance()  # Consume next token.
                if self._lexer.token().type != token.NAME:
                    continue

                if self._is_maya_command():
                    self._command_flags += filter(None, [self._parse_command_flags(self._lexer.token().string)])
                    continue

            except StopIteration:
                break

    def _parse_command_flags(self, command_name: str) -> flags.FlagKwargs:
        """Parse command args.

        Args:
            command_name: Name of maya command.

        Returns:
            list: Kwargs object representing found maya flags token data.

        """
        flag_tokens = []
        scope = 0
        while True:
            try:
                self._lexer.advance()  # Consume next token.
                # We need to keep operators for scope tracking.
                if self._lexer.token().type not in (token.OP, token.NAME):
                    continue

                if self.toke_equal_to(self._lexer.token(), token.OP, "("):
                    scope += 1
                    continue
                elif self.toke_equal_to(self._lexer.token(), token.OP, ")"):
                    scope -= 1
                    continue

                if self._is_maya_command():
                    flag_tokens += filter(
                        None,
                        [self._parse_command_flags(self._lexer.token().string)],
                    )
                    continue

                if scope > 1:
                    # An open parenthesis we don't want to account for has been open.
                    # Continue until the scope hase been closed.
                    continue

                if scope == 0:  # End of maya command function.
                    break

                if self._is_maya_flag(command_name):
                    flag_tokens.append(
                        flags.create_flag_arg(
                            self._lexer.token(),
                            self._config.get_flags(command_name).get(self._lexer.token().string, ""),
                        )
                    )
                    continue

            except StopIteration:
                break

        return flags.FlagKwargs(command_name=command_name, flag_tokens=flag_tokens) if flag_tokens else None

    @staticmethod
    def toke_equal_to(tok: tokenize.TokenInfo, type_: int, text: str = "") -> bool:
        """Check if token matches expected values.

        Args:
            tok: Token to check.
            type_: Token type to compare.
            text (str, optional): Text value to compare.

        Returns:
            True if token matches expected values else False.

        """
        return tok.type == type_ and tok.string == text if text else True

    def _is_maya_command(self) -> bool:
        """Check if current token is maya command.

        Returns:
            True if maya command found else False.

        """
        if not (self._found_maya_modules and self._is_maya_module()):
            return False

        # If the code has reached this far we know that whatever `cmds` has been imported as and a `.` is behind us
        # E.g `cmds.`.
        self._lexer.advance()  # Consume final token e.g maya command name.
        return bool(self._config.get_flags(self._lexer.token().string) and self.toke_equal_to(self._lexer.peek(), token.OP, "("))

    def _is_maya_flag(self, command_name: str) -> bool:
        """Check if current token is maya flag name.

        Args:
            command_name: Maya command name to check flag for.

        Returns:
            True if current token is maya flag else False.

        """
        return (
            self._lexer.token().type == token.NAME
            and self._config.get_flags(command_name).get(self._lexer.token().string)
            and self.toke_equal_to(self._lexer.peek(), token.OP, "=")
        )

    def _is_maya_module(self) -> bool:
        """Check if cmds module found."""
        if not self._found_maya_modules or self._lexer.token().type != token.NAME:
            return False

        module_string = self._lexer.token().string
        maya_module_paths = [f"{m}." for m in self._found_maya_modules]  # Add a dot at the end.

        while True:
            # Consume tokens until we no longer match import maya module.
            if any(m.startswith(module_string + self._lexer.peek().string) for m in maya_module_paths):
                self._lexer.advance()
                module_string += self._lexer.token().string
            else:
                break

        return module_string in maya_module_paths

    def _parse_maya_imports(self, source_code: str, file_name: str) -> None:
        """Check if maya is imported is source code.

        Args:
            source_code: Source code to parse.
            file_name: File path to source.

        """
        tree = ast.parse(source_code, file_name)
        import_visitor = MayaImportVisitor(self._config.modules)
        import_visitor.visit(tree)
        self._found_maya_modules = import_visitor.maya_imports
