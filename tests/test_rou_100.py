# Pip imports
import pytest

# Internal imports
from tests.helpers import results


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
