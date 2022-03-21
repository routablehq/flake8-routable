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

ROU100 = "ROU100 Use triple double quotes for docstrings"
ROU101 = "ROU101 Import from a tests directory"


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors = []

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None and "tests" in node.module:
            self.errors.append((node.lineno, node.col_offset, ROU101))


class Plugin:
    """Flake8 plugin to find doc strings defined with invalid characters."""

    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree, file_tokens: List[tokenize.TokenInfo]) -> None:
        self._file_tokens = file_tokens
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type["Plugin"]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)

        errors = chain(self._lines_with_invalid_docstrings(), visitor.errors)

        for line_no in errors:
            yield line_no, 0, ROU100, type(self)

    def _lines_with_invalid_docstrings(self) -> Generator[int, None, None]:
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
                    yield line_no
            # encountered a statement declaration, save its line number
            elif token_type == tokenize.NAME and token_str in DOCSTRING_STMT_TYPES:
                last_stmt_line_no = line_no
            # encountered a hash comment that is a docstring
            elif token_type == tokenize.COMMENT and last_stmt_line_no is not None and last_stmt_line_no + 1 == line_no:
                yield line_no

            # grouped tokens will no longer be a comment's prefix if they aren't new lines or indents (earlier clause)
            is_comment_prefix = False
