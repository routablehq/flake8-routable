# Python imports
import ast
import importlib.metadata as importlib_metadata
import tokenize
from itertools import chain
from typing import Generator, List, Tuple, Type


DOCSTRING_STMT_TYPES = (
    "class",
    "def",
)

ROU100 = "ROU100 Triple double quotes not used for docstring"
ROU101 = "ROU101 Import from a tests directory"


class Visitor(ast.NodeVisitor):
    """Linting errors that use the AST."""

    def __init__(self) -> None:
        self.errors = []

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None and "tests" in node.module:
            self.errors.append((node.lineno, node.col_offset, ROU101))


class FileTokenHelper:
    """Linting errors that use file tokens."""

    def __init__(self) -> None:
        self.errors = []
        self._file_tokens = []

    def vist(self, file_tokens: List[tokenize.TokenInfo]) -> None:
        self._file_tokens = file_tokens

        # run methods that generate errors using file tokens
        self.lines_with_invalid_docstrings()

    def lines_with_invalid_docstrings(self) -> None:
        """
        Yield the physical line number of a docstring commented without triple-double-quotes.

        This applies to class, function, and method statements.

        To find a docstring iterate through a file, keep track of the line numbers of those
        applicable statements, and if a comment happens the line after then you are looking
        at a docstring.

        Comments can happen on code immediately following a statement definition but this is
        rare, unusual, and most likely warranting the inclusion of a docstring.
        """
        is_comment_prefix = False
        last_stmt_line_no = None

        for token_type, token_str, start_indices, _, line in self._file_tokens:
            line_no = start_indices[0]
            # XXX print((token_type, token_str, start_indices, line))

            if token_type in (tokenize.NEWLINE, tokenize.NL, tokenize.INDENT):
                is_comment_prefix = True
                continue

            # encountered an indented string
            if token_type == tokenize.STRING and is_comment_prefix:
                # encountered triple-single-quote docstring
                if (
                    last_stmt_line_no is not None
                    and last_stmt_line_no + 1 == line_no
                    and line.strip().startswith("'''")
                ):
                    self.errors.append((*start_indices, ROU100))
            # encountered a statement declaration, save its line number
            elif token_type == tokenize.NAME and token_str in DOCSTRING_STMT_TYPES:
                last_stmt_line_no = line_no
            # encountered a hash comment that is a docstring
            elif token_type == tokenize.COMMENT and last_stmt_line_no is not None and last_stmt_line_no + 1 == line_no:
                self.errors.append((*start_indices, ROU100))

            # grouped tokens will no longer be a comment's prefix if they aren't new lines or indents (earlier clause)
            is_comment_prefix = False


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
