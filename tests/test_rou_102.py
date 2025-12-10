# Pip imports
import pytest

# Internal imports
from tests.helpers import results


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
