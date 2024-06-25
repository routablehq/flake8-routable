# Python imports
import ast
import importlib.metadata as importlib_metadata
import re
import tokenize
import warnings
from dataclasses import dataclass
from itertools import chain
from typing import Any, Generator, List, Tuple, Type, Union


CLASS_AND_FUNC_TOKENS = (
    "class",
    "def",
)

MAX_BLANK_LINES_AFTER_COMMENT = 2

# comments to ignore, including section headers
IGNORABLE_COMMENTS = (
    "# ==",
    "# --",
    "# 2020-04-06 - Needs review",
)

# Note: The rule should be what is wrong, not how to fix it
ROU100 = "ROU100 Triple double quotes not used for docstring"
ROU101 = "ROU101 Import from a tests directory"
ROU102 = "ROU102 Strings should not span multiple lines except comments or docstrings"
ROU103 = "ROU103 Object does not have attributes in order"
ROU104 = "ROU104 Multiple blank lines are not allowed after a non-section comment"
ROU105 = "ROU105 Constants are not in order"
ROU106 = "ROU106 Relative imports are not allowed"
ROU107 = "ROU107 Inline function import is not at top of statement"
ROU108 = "ROU108 Import from model module instead of sub-packages"
ROU109 = "ROU109 Disallow rename migrations"
ROU110 = "ROU110 Disallow .save() with no update_fields"
ROU111 = "ROU111 Disallow FeatureFlag creation in code"
ROU112 = "ROU112 Tasks mush have *args, **kwargs"
ROU113 = "ROU113 Tasks can not have priority in the signature"


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

        self._constant_nodes = []
        self._last_constant_end_lineno = None

    def _check_constant_order(self, group: List[ast.Assign]):
        group_strings = [node.targets[0].id.replace("_", " ") for node in group]
        if sorted(group_strings) != group_strings:
            self.errors.append((group[0].lineno, group[0].col_offset, ROU105))

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
            warnings.warn(f"Could not parse {type(node)}")
            return ""
        return str(value)

    def finalize(self):
        """Run methods after every node has been visited"""
        self._check_constant_order(self._constant_nodes)

    def visit(self, node: ast.AST) -> Any:
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, None)
        if not visitor:
            return self.generic_visit(node)
        visitor(node)
        return self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> Any:
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id.isupper():
            if self._last_constant_end_lineno != node.lineno - 1:
                self._check_constant_order(self._constant_nodes)
                self._constant_nodes = []

            self._constant_nodes.append(node)
            self._last_constant_end_lineno = node.end_lineno

    def visit_Dict(self, node: ast.Dict) -> None:
        if None not in node.keys and not self._is_ordered(node.keys):
            self.errors.append((node.lineno, node.col_offset, ROU103))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        has_non_docstring_before_import = False
        for i, body_node in enumerate(node.body):
            # ignore docstrings
            if isinstance(body_node, ast.Expr) and i == 0:
                continue
            # note we hit an import statement
            elif isinstance(body_node, ast.ImportFrom):
                if has_non_docstring_before_import:
                    self.errors.append((body_node.lineno, body_node.col_offset, ROU107))
            else:
                has_non_docstring_before_import = True

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None and "tests" in node.module:
            self.errors.append((node.lineno, node.col_offset, ROU101))

        if node.level > 0:
            self.errors.append((node.lineno, node.col_offset, ROU106))

        if node.module is not None and ".models." in node.module:
            self.errors.append((node.lineno, node.col_offset, ROU108))

    def visit_Set(self, node: ast.Set) -> None:
        if not self._is_ordered(node.elts):
            self.errors.append((node.lineno, node.col_offset, ROU103))


class FileTokenHelper:
    """Linting errors that use file tokens."""

    def __init__(self) -> None:
        self.errors = []
        self._file_tokens = []

    def visit(self, file_tokens: List[tokenize.TokenInfo]) -> None:
        self._file_tokens = file_tokens

        # run methods that generate errors using file tokens
        self.lines_with_blank_lines_after_comments()
        self.lines_with_invalid_docstrings()
        self.lines_with_invalid_multi_line_strings()
        self.rename_migrations()
        self.disallow_no_update_fields_save()
        self.disallow_feature_flag_creation()
        self.task_args_kwargs_and_priority()

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
            # Condition 6: Not a class/function statement, statement decorator, or section after dedent
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
                # Condition 5b: Not a dedent, ignorable comment, ignore
                elif token_type == tokenize.COMMENT and token_str.startswith(IGNORABLE_COMMENTS):
                    do_reset_conditions = True
                # Condition 5c: Not a dedent, not an ignorable comment, this meets enough conditions to be an error
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
                and not token_str.startswith(IGNORABLE_COMMENTS)
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

        for token_type, token_str, start_indices, end_indices, line in self._file_tokens:
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

    def rename_migrations(self) -> None:
        """Migrations should not allow renames."""
        reported = set()
        disallowed_migration_text = "migrations.RenameField"

        for line_token in self._file_tokens:
            if line_token.start[0] in reported:
                # There could be many tokens on a same line.
                continue

            if disallowed_migration_text in line_token.line:
                reported.add(line_token.start[0])
                self.errors.append((*line_token.start, ROU109))

    def disallow_no_update_fields_save(self) -> None:
        """.save() must be called with update_fields."""
        reported = set()
        single_line_save = re.compile(r".+(\.save\(.*)")
        allowed_comments = [
            "# TODO: needs fix",
            "# file save",
            "# form save",
            "# ledger save",
            "# multi-line with update_fields",
            "# new model save",
            "# not a model",
            "# save extension",
            "# serializer save",
        ]

        for line_token in self._file_tokens:
            if line_token.start[0] in reported:
                # There could be many tokens on a same line.
                continue

            line = line_token.line

            if not single_line_save.match(line):
                # Skip lines that don't match
                continue

            if "update_fields" in line:
                # save, with update_fields is allowed
                continue

            if any(comment in line for comment in allowed_comments):
                # Ignore lines with these comments, as they are valid
                continue

            reported.add(line_token.start[0])
            self.errors.append((*line_token.start, ROU110))

    def disallow_feature_flag_creation(self) -> None:
        """We can not create FeatureFlags in code, they are cached on the request."""
        reported = set()
        feature_flag_creation = re.compile(r"^.*?(FeatureFlag\.objects\..*create)")
        allowed_comments = [
            "# valid for legacy cross-border work",
            "# valid for management command",
        ]

        for line_token in self._file_tokens:
            if line_token.start[0] in reported:
                # There could be many tokens on a same line.
                continue

            line = line_token.line

            if not feature_flag_creation.match(line):
                # Skip lines that don't match
                continue

            if any(comment in line for comment in allowed_comments):
                # Ignore lines with these comments, as they are valid
                continue

            reported.add(line_token.start[0])
            self.errors.append((*line_token.start, ROU111))

    def task_args_kwargs_and_priority(self) -> None:
        """Don't allow tasks without args or kwargs."""
        handler_start = False
        in_task_definition = False
        args_found = False
        kwargs_found = False
        last_star = -1
        last_star_star = -1

        for i, (token_type, token_str, start_indices, end_indices, line) in enumerate(self._file_tokens):
            # Start of a contextmanager
            if token_type == tokenize.OP and token_str == "@":
                handler_start = True
            # It is a shared_task
            elif handler_start and token_type == tokenize.NAME and token_str == "shared_task":
                in_task_definition = True

            # Track * and ** positions
            elif in_task_definition and token_type == tokenize.OP and token_str == "*":
                last_star = i
            elif in_task_definition and token_type == tokenize.OP and token_str == "**":
                last_star_star = i

            # Look for *args and **kwargs
            elif in_task_definition and token_type == tokenize.NAME and token_str == "args" and last_star == i - 1:
                args_found = True
            elif (
                in_task_definition and token_type == tokenize.NAME and token_str == "kwargs" and last_star_star == i - 1
            ):
                kwargs_found = True

            # Check for priority in the signature
            elif in_task_definition and token_type == tokenize.NAME and token_str == "priority":
                self.errors.append((*start_indices, ROU113))

            # End of method, are *args or **kwargs missing?
            elif token_type == tokenize.OP and token_str == ":":
                if in_task_definition and (not args_found or not kwargs_found):
                    self.errors.append((*start_indices, ROU112))

                handler_start = False
                in_task_definition = False
                args_found = False
                kwargs_found = False


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
        visitor.finalize()

        file_token_helper = FileTokenHelper()
        file_token_helper.visit(self._file_tokens)

        for line, col, msg in chain(visitor.errors, file_token_helper.errors):
            yield line, col, msg, type(self)
