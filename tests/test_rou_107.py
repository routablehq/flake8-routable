# Pip imports
import pytest

# Internal imports
from tests.helpers import results


class TestROU107:
    LOWER_IMPORT_FUNCTION = (
        "def foo():\n" '    """ This is a lovely docstring. """\n' "    x = 4\n" "\n" "    from bar import baz\n"
    )

    LOWER_IMPORT_METHOD = (
        "class Foo:\n"
        "    def assign_things(self):\n"
        '        """\n'
        "        Multi-line docstring\n"
        "        is happening here\n"
        '        """\n'
        "\n"
        '        thing_levels = self.thing_settings and self.thing_settings.get("levels")\n'
        "        if not thing_levels:\n"
        "            thing_levels = []\n"
        "\n"
        "        # Internal imports\n"
        "        from some.little.logic import thing\n"
    )

    LOWER_IMPORT_METHOD_NESTED_FUNC = (
        "class Foo:\n"
        "    def foo(self):\n"
        '        """ This is a lovely docstring. """\n'
        "        x = 4\n"
        "\n"
        "        def bar(y):\n"
        "            from baz import qux\n"
        "\n"
        "            return y*qux(y)\n"
        "\n"
        "        return bar(x)\n"
    )

    UPPER_DOUBLE_IMPORT_METHOD = (
        "def foo(self, bar):\n"
        "\n"
        "    # Internal imports\n"
        "    from little.thing import BigThing\n"
        "    from big.thing import LittleThing\n"
    )

    UPPER_IMPORT_FUNCTION = (
        "def foo():\n" '    """ This is a lovely docstring. """\n' "    from bar import baz\n" "\n" "    x = 4\n"
    )

    UPPER_IMPORT_METHOD_DOCSTRING = (
        "class Foo:\n"
        "    def foo(self):\n"
        '        """ This is a lovely docstring. """\n'
        "        from bar import baz\n"
        "\n"
        "        x = 4\n"
    )

    def test_lower_import_function(self):
        error = results(self.LOWER_IMPORT_FUNCTION)
        assert error == {"5:4: ROU107 Inline function import is not at top of statement"}

    def test_lower_import_method(self):
        error = results(self.LOWER_IMPORT_METHOD)
        assert error == {"13:8: ROU107 Inline function import is not at top of statement"}

    @pytest.mark.parametrize(
        "upper_import",
        (
            LOWER_IMPORT_METHOD_NESTED_FUNC,
            UPPER_DOUBLE_IMPORT_METHOD,
            UPPER_IMPORT_FUNCTION,
            UPPER_IMPORT_METHOD_DOCSTRING,
        ),
    )
    def test_upper_imports(self, upper_import):
        error = results(upper_import)
        assert error == set()
