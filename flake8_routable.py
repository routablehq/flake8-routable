# Python imports
import ast
import importlib.metadata as importlib_metadata
import tokenize
from itertools import chain
from typing import Any, Generator, List, Tuple, Type, Union


DOCSTRING_STMT_TYPES = (
    "class",
    "def",
)

# Note: The rule should be what is wrong, not how to fix it
ROU100 = "ROU100 Triple double quotes not used for docstring"
ROU101 = "ROU101 Import from a tests directory"
ROU102 = "ROU102 Strings should not span multiple lines except comments or docstrings"
ROU103 = "ROU103 Object does not have attributes in order"
ROU200 = "ROU200 Could not parse"


class Visitor(ast.NodeVisitor):
    """Linting errors that use the AST."""

    def __init__(self) -> None:
        self.errors = []

    def _is_ordered(self, values: List[Any]) -> bool:
        stringify = [self._parse_to_string(value).lower() for value in values]
        return sorted(stringify) == stringify

    def _parse_Attribute(self, node: Union[ast.Attribute, ast.Name], s="") -> str:
        if isinstance(node, ast.Attribute):
            return self._parse_Attribute(node.value, s=f".{node.attr}{s}")
        return f"{self._parse_to_string(node)}{s}"

    def _parse_to_string(self, node):
        if isinstance(node, ast.Attribute):
            value = self._parse_Attribute(node)
        elif isinstance(node, ast.Call):
            value = self._parse_to_string(node.func)
        elif isinstance(node, ast.Constant):
            value = node.value
        elif isinstance(node, ast.Name):
            value = node.id
        elif isinstance(node, ast.JoinedStr):
            value = "".join([self._parse_to_string(value) for value in node.values])
        elif isinstance(node, ast.Tuple):
            value = "".join([self._parse_to_string(elt) for elt in node.elts])
        elif hasattr(node, "value"):
            value = self._parse_to_string(node.value)
        else:
            self.errors.append((node.lineno, node.col_offset, f"ROU200 could not parse {type(node)}"))
            return ""
        return str(value)

    def visit_Dict(self, node: ast.Dict) -> None:
        if None not in node.keys and not self._is_ordered(node.keys):
            self.errors.append((node.lineno, node.col_offset, ROU103))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None and "tests" in node.module:
            self.errors.append((node.lineno, node.col_offset, ROU101))

    def visit_Set(self, node: ast.Set) -> None:
        if not self._is_ordered(node.elts):
            self.errors.append((node.lineno, node.col_offset, ROU103))


class FileTokenHelper:
    """Linting errors that use file tokens."""

    def __init__(self) -> None:
        self.errors = []
        self._file_tokens = []

    def vist(self, file_tokens: List[tokenize.TokenInfo]) -> None:
        self._file_tokens = file_tokens

        # run methods that generate errors using file tokens
        self.lines_with_invalid_docstrings()
        self.lines_with_invalid_multi_line_strings()

    def lines_with_invalid_multi_line_strings(self) -> None:
        """
        Multi-line strings should be single-quoted strings concatenated across multiple lines,
        not with triple-quotes.

        To find a multi-line string with triple-quotes look for a string that spans multiple
        lines that is not occurring immediately after a statement definition.
        """
        is_whitespace_prefix = False

        for i, (token_type, token_str, start_indices, end_indices, line) in enumerate(self._file_tokens):
            if token_type in (
                tokenize.DEDENT,
                tokenize.INDENT,
                tokenize.NEWLINE,
                tokenize.NL,
            ):
                is_whitespace_prefix = True
                continue

            # Encountered a multi-line string assignment that is not a docstring.
            # It could also be the first line of a line of the file.
            if (
                token_type == tokenize.STRING
                and token_str.startswith(("'''", '"""'))
                and token_str.endswith(("'''", '"""'))
                and end_indices[0] > start_indices[0]
                and not is_whitespace_prefix
                and i > 0
            ):
                self.errors.append((*start_indices, ROU102))

            is_whitespace_prefix = False

    def lines_with_invalid_docstrings(self) -> None:
        """
        A docstring should contain triple-double-quotes and applies to
        classes, functions, and methods.

        To find a docstring iterate through a file, keep track of the line numbers of those
        applicable statements, and if a comment happens the line after then you are looking
        at a docstring.

        Comments can happen on code immediately following a statement definition but this is
        rare, unusual, and most likely warranting the inclusion of a docstring.
        """
        is_whitespace_prefix = False
        is_inside_stmt = False

        # last line number of the last statement (in case it spans multiple lines)
        last_stmt_line_no = None

        for (token_type, token_str, start_indices, end_indices, line) in self._file_tokens:
            line_no = start_indices[0]

            if token_type in (tokenize.DEDENT, tokenize.INDENT, tokenize.NEWLINE, tokenize.NL):
                is_whitespace_prefix = True
                continue

            # encountered an indented string
            if token_type == tokenize.STRING and is_whitespace_prefix:
                # encountered triple-single-quote docstring
                if (
                    last_stmt_line_no is not None
                    and last_stmt_line_no + 1 == line_no
                    and line.strip().startswith("'''")
                ):
                    self.errors.append((*start_indices, ROU100))
            # encountered a statement declaration, save its line number
            elif token_type == tokenize.NAME and token_str in DOCSTRING_STMT_TYPES:
                is_inside_stmt = True
            # encountered the end of a statement declaration, save the line number
            elif token_type == tokenize.OP and is_inside_stmt and token_str == ":":
                last_stmt_line_no = line_no
                is_inside_stmt = False
            # encountered a hash comment that is a docstring
            elif (
                token_type == tokenize.COMMENT
                and last_stmt_line_no is not None
                and last_stmt_line_no + 1 == line_no
                and is_whitespace_prefix
            ):
                self.errors.append((*start_indices, ROU100))

            # grouped tokens will no longer be a comment's prefix if they aren't new lines or indents (earlier clause)
            is_whitespace_prefix = False


class Plugin:
    """Flake8 plugin for Routable's best coding practices."""

    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree, file_tokens: List[tokenize.TokenInfo]) -> None:
        self._file_tokens = file_tokens
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type["Plugin"]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)

        file_token_helper = FileTokenHelper()
        file_token_helper.vist(self._file_tokens)

        for line, col, msg in chain(visitor.errors, file_token_helper.errors):
            yield line, col, msg, type(self)
