# Python imports
import ast
import importlib.metadata as importlib_metadata
import tokenize
from dataclasses import dataclass
from itertools import chain
from typing import Generator, List, Tuple, Type


CLASS_AND_FUNC_TOKENS = (
    "class",
    "def",
)

MAX_BLANK_LINES_AFTER_COMMENT = 2
SECTION_COMMENT_STARTS = (
    "# ==",
    "# --",
)

# Note: The rule should be what is wrong, not how to fix it
ROU100 = "ROU100 Triple double quotes not used for docstring"
ROU101 = "ROU101 Import from a tests directory"
ROU102 = "ROU102 Strings should not span multiple lines except comments or docstrings"
ROU104 = "ROU104 Multiple blank lines are not allowed after a non-section comment"


@dataclass
class BlankLinesAfterCommentConditions:
    # Comment that is a section comment
    section_comment: bool = True

    # New line after comment
    nl1_after_comment: bool = False

    # Another new line after comment
    nl2_after_comment: bool = False

    # Another new line after comment
    nl3_after_comment: bool = False

    # A dedent
    dedent: bool = False

    # A class/function statement or statement decorator after dedent
    stmt_or_decorator: bool = True

    def is_all_passed(self):
        return (
            not self.section_comment
            and self.nl1_after_comment
            and self.nl2_after_comment
            and self.nl3_after_comment
            and self.dedent
            and not self.stmt_or_decorator
        )


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
        self.lines_with_blank_lines_after_comments()
        self.lines_with_invalid_docstrings()
        self.lines_with_invalid_multi_line_strings()

    def lines_with_blank_lines_after_comments(self) -> None:
        """
        Comments should not have more than one blank line after them.

        The exception to this rule is if a comment is a section comment like so:
            # -----------------
            # Section Comment
            # -----------------
        """
        # A bit array representing all the conditions it takes for an error to be found
        # (see inline comments below on conditions)
        conditions = BlankLinesAfterCommentConditions()

        for i, (token_type, token_str, start_indices, _, _) in enumerate(self._file_tokens):
            do_reset_conditions = False

            # Dedenting in progress
            if conditions.dedent and conditions.stmt_or_decorator and token_type == tokenize.DEDENT:
                continue
            # Condition 6: Not a class/function statement or statement decorator after dedent
            elif (
                conditions.dedent
                and not (token_type == tokenize.NAME and token_str in CLASS_AND_FUNC_TOKENS)
                and not (token_type == tokenize.OP and token_str == "@")
            ):
                conditions.stmt_or_decorator = False
            elif conditions.nl3_after_comment and not conditions.dedent:
                # Condition 5a: A dedent
                if token_type == tokenize.DEDENT:
                    conditions.dedent = True
                # Condition 5b: Not a dedent, this meets enough conditions to be an error
                else:
                    conditions.dedent = True
                    conditions.stmt_or_decorator = False

                    # we want to use previous start_indices where the double new-line was found
                    start_indices = self._file_tokens[i - 1][2]
            # Condition 4: Another new line after comment
            elif conditions.nl2_after_comment and not conditions.nl3_after_comment and token_type == tokenize.NL:
                conditions.nl3_after_comment = True
            # Condition 3: Another new line after comment
            elif conditions.nl1_after_comment and not conditions.nl2_after_comment and token_type == tokenize.NL:
                conditions.nl2_after_comment = True
            # Condition 2: New line after comment
            elif not conditions.section_comment and not conditions.nl1_after_comment and token_type == tokenize.NL:
                conditions.nl1_after_comment = True
            # Condition 1: Comment that is not a section comment
            elif (
                conditions.section_comment
                and token_type == tokenize.COMMENT
                and not token_str.startswith(SECTION_COMMENT_STARTS)
            ):
                conditions.section_comment = False
            else:
                do_reset_conditions = True

            if conditions.is_all_passed():
                do_reset_conditions = True
                self.errors.append((*start_indices, ROU104))

            if do_reset_conditions:
                conditions = BlankLinesAfterCommentConditions()

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
            elif token_type == tokenize.NAME and token_str in CLASS_AND_FUNC_TOKENS:
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
