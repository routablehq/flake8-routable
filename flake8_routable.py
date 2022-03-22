import sys
import tokenize
from typing import Generator, List, Tuple, Type

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

DOCSTRING_STMT_TYPES = (
    "class",
    "def",
)

ROU100 = "ROU100 Use triple double quotes for docstrings"
ROU101 = "ROU101 Multi-line strings should only be reserved for comments or docstrings"


class Plugin:
    """Flake8 plugin to find doc strings defined with invalid characters."""

    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree, file_tokens: List[tokenize.TokenInfo]) -> None:
        self._file_tokens = file_tokens
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type["Plugin"]], None, None]:
        for line_no in self._lines_with_invalid_docstrings():
            yield line_no, 0, ROU100, type(self)

        for line_no in self._lines_with_invalid_multi_line_strings():
            yield line_no, 0, ROU101, type(self)

    def _lines_with_invalid_multi_line_strings(self) -> Generator[int, None, None]:
        """
        Yields the phsyical line number of an invalid multi-line string.

        Multi-line strings should be single-quoted strings concatenated across multiple lines,
        not with triple-quotes.

        To find a multi-line string with triple-quotes look for a string that spans multiple
        lines that is not occurring immediately after a statement definition.
        """
        is_whitespace_prefix = False

        for i, (token_type, token_str, start_indices, end_indices, line) in enumerate(
            self._file_tokens
        ):
            line_no = start_indices[0]

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
                yield line_no

            is_whitespace_prefix = False

    def _lines_with_invalid_docstrings(self) -> Generator[int, None, None]:
        """
        Yields the physical line number of a docstring commented without triple-double-quotes.

        This applies to class, function, and method statements.

        To find a docstring iterate through a file, keep track of the line numbers of those
        applicable statements, and if a comment happens the line after then you are looking
        at a docstring.

        Comments can happen on code immediately following a statement definition but this is
        rare, unusual, and most likely warranting the inclusion of a docstring. We will error
        on this.
        """
        is_whitespace_prefix = False
        is_inside_stmt = False

        # last line number of the last statement (in case it spans multiple lines)
        last_stmt_line_no = None

        for (
            token_type,
            token_str,
            start_indices,
            end_indices,
            line,
        ) in self._file_tokens:
            line_no = start_indices[0]

            if token_type in (
                tokenize.DEDENT,
                tokenize.INDENT,
                tokenize.NEWLINE,
                tokenize.NL,
            ):
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
                    yield line_no
            # encountered a statement declaration, flag we are in there
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
                yield line_no

            # grouped tokens will no longer be a comment's prefix if they aren't new lines or indents (earlier clause)
            is_whitespace_prefix = False
