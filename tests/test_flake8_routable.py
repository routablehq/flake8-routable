# Python imports
import ast
import io
import tokenize

# Pip imports
import pytest

# Internal imports
from flake8_routable import Plugin


def results(s):
    return {
        "{}:{}: {}".format(*r)
        for r in Plugin(ast.parse(s), list(tokenize.generate_tokens(io.StringIO(s).readline))).run()
    }


class TestROU100:
    CLASS_DOCSTRING_TRIPLE_DOUBLE_QUOTES = (
        "class Foo:\n" '    """ What a lovely docstring with lots of things to be talking about"""\n' "    pass\n"
    )

    CLASS_DOCSTRING_TRIPLE_SINGLE_QUOTES = (
        "class Foo:\n" "    ''' Single triple quotes for a docstring explaining things? Oh no. '''\n" "    pass\n"
    )

    CLASS_DOCSTRING_HASH = (
        "class Foo:\n" "    # Hash mon? Not as a docstring, try again with triple double quotes\n" "    pass\n"
    )

    FUNC_DOCSTRING_TRIPLE_DOUBLE_QUOTES = (
        "def foo(x, y):\n"
        '    """ What a lovely docstring with lots of things to be talking about """\n'
        "    return x + y\n"
    )

    FUNC_DOCSTRING_TRIPLE_SINGLE_QUOTES = (
        "def foo(x, y):\n"
        "    ''' Single triple quotes for a docstring explaining things? Oh no.?! '''\n"
        "    return x + y\n"
    )

    FUNC_DOCSTRING_TRIPLE_SINGLE_QUOTES_MULTI_LINE = (
        "def foo(\n"
        "    one_really_long_argument,\n"
        "    another_really_long_argument\n"
        "):\n"
        "    ''' Single quotes?! '''\n"
        "    return x + y\n"
    )

    FUNC_DOCSTRING_HASH = (
        "def foo(x, y):\n"
        "    # Hash mon? Not as a docstring, try again with triple double quotes\n"
        "    return x + y\n"
    )

    FUNC_IGNORE_INLINE_HASH = (
        "def foo(x, y):\n"
        "    if x % 2 == 0: # TODO: why does this matter if it's even again?\n"
        "        return x\n"
        "\n"
        "    return y\n"
    )

    METHOD_DOCSTRING_HASH = "class Bar:\n" "    def __init__(self, x):\n" "        # Hash mon?\n" "        self.x = x\n"

    METHOD_DOCSTRING_TRIPLE_DOUBLE_QUOTES = (
        "class Bar:\n" "   def __init__(self, x):\n" '       """ What a lovely docstring """\n' "       self.x = x\n"
    )

    METHOD_DOCSTRING_TRIPLE_SINGLE_QUOTES = (
        "class Bar:\n" "    def __init__(self, x):\n" "        ''' Single quotes?! '''\n" "        self.x = x\n"
    )

    @pytest.mark.parametrize(
        "doc_string",
        (
            CLASS_DOCSTRING_TRIPLE_DOUBLE_QUOTES,
            FUNC_DOCSTRING_TRIPLE_DOUBLE_QUOTES,
            METHOD_DOCSTRING_TRIPLE_DOUBLE_QUOTES,
        ),
    )
    def test_correct_docstring(self, doc_string):
        errors = results(doc_string)
        assert errors == set()

    @pytest.mark.parametrize("doc_string", (CLASS_DOCSTRING_TRIPLE_SINGLE_QUOTES, CLASS_DOCSTRING_HASH))
    def test_incorrect_docstring_class(self, doc_string):
        errors = results(doc_string)
        assert errors == {"2:4: ROU100 Triple double quotes not used for docstring"}

    @pytest.mark.parametrize("doc_string", (FUNC_DOCSTRING_HASH, FUNC_DOCSTRING_TRIPLE_SINGLE_QUOTES))
    def test_incorrect_docstring_function(self, doc_string):
        errors = results(doc_string)
        assert errors == {"2:4: ROU100 Triple double quotes not used for docstring"}

    def test_ignore_hash_comment(self):
        errors = results(self.FUNC_IGNORE_INLINE_HASH)
        assert errors == set()

    @pytest.mark.parametrize("doc_string", (METHOD_DOCSTRING_TRIPLE_SINGLE_QUOTES, METHOD_DOCSTRING_HASH))
    def test_incorrect_docstring_method(self, doc_string):
        errors = results(doc_string)
        assert errors == {"3:8: ROU100 Triple double quotes not used for docstring"}

    def test_incorrect_docstring_multi_line_function(self):
        errors = results(self.FUNC_DOCSTRING_TRIPLE_SINGLE_QUOTES_MULTI_LINE)
        assert errors == {"5:4: ROU100 Triple double quotes not used for docstring"}


class TestROU101:
    def test_correct_no_import_from_tests(self):
        errors = results("from foo.bar import baz")
        assert errors == set()

    def test_incorrect_import_from_tests(self):
        errors = results("from foo.tests import bar")
        assert errors == {"1:0: ROU101 Import from a tests directory"}


class TestROU102:
    INVALID_MULTI_LINE_STRING = (
        "def foo(x, y):\n"
        "\n"
        '    copy = """This is the text\n'
        "    that is spanning multiple lines,\n"
        '    now good bye."""\n'
        "\n"
        '    return f"{x} {y} {copy}"\n'
    )

    MULTI_LINE_COMMENT = (
        "class Foo:\n"
        "\n"
        "    def foo(self, y):\n"
        '        """ Get some things, do some stuff. """\n'
        "        z = x + y\n"
        "\n"
        '        """\n'
        "        This is a multi-line comment\n"
        "        just talking about things and stuff.\n"
        "        Ignore me.\n"
        '        """\n'
        "\n"
        "        return z\n"
    )

    MULTI_LINE_COMMENT_START = '"""hello there,\nhi"""\n'

    MULTI_LINE_DOCSTRING = (
        "def foo(x, y):\n"
        '    """\n'
        "    I am a docstring,\n"
        "    leave me alone!\n"
        '    """\n'
        "    return x + y\n"
    )

    MULTI_LINE_STRING = (
        "def foo(x, y):\n"
        "\n"
        "    copy = (\n"
        '        "This is the text "\n'
        '        "that is spanning multiple lines, "\n'
        '        "now good bye."\n'
        "    )\n"
        "\n"
        '    return f"{x} {y} {copy}"\n'
    )

    @pytest.mark.parametrize(
        "multi_line_string",
        (
            MULTI_LINE_COMMENT,
            MULTI_LINE_COMMENT_START,
            MULTI_LINE_DOCSTRING,
            MULTI_LINE_STRING,
        ),
    )
    def test_correct_multi_line_string(self, multi_line_string):
        errors = results(multi_line_string)
        assert errors == set()

    def test_incorrect_multi_line_string(self):
        errors = results(self.INVALID_MULTI_LINE_STRING)
        assert errors == {"3:11: ROU102 Strings should not span multiple lines except comments or docstrings"}


class TestROU104:
    def test_incorrect_blank_lines_after_comment(self):
        errors = results("# Setup\n\n\nUser = get_user_model()\n")
        assert errors == {"3:0: ROU104 Multiple blank lines are not allowed after a comment"}

    def test_correct_blank_line_after_comment(self):
        errors = results("# Setup\n\nUser = get_user_model()\n")
        assert errors == set()

    def test_correct_blank_lines_after_section(self):
        errors = results("# -------\n# Tests\n# -------\n\n\nX = 4")
        assert errors == set()
