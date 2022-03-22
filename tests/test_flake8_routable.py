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
    CLASS_DOC_STRING_TRIPLE_DOUBLE_QUOTES = '''
class Foo:
    """ What a lovely docstring """
    pass
    '''

    CLASS_DOC_STRING_TRIPLE_SINGLE_QUOTES = """
class Foo:
    ''' Single quotes?! '''
    pass
    """

    CLASS_DOC_STRING_HASH = """
class Foo:
    # Hash mon?
    pass
    """

    FUNC_DOC_STRING_TRIPLE_DOUBLE_QUOTES = '''
def foo(x, y):
    """ What a lovely docstring """
    return x + y
    '''

    FUNC_DOC_STRING_TRIPLE_SINGLE_QUOTES = """
def foo(x, y):
    ''' Single quotes?! '''
    return x + y
    """

    FUNC_DOC_STRING_HASH = """
def foo(x, y):
    # Hash mon?
    return x + y
    """

    METHOD_DOC_STRING_TRIPLE_DOUBLE_QUOTES = '''
class Bar:
    def __init__(self, x):
        """ What a lovely docstring """
        self.x = x
    '''

    METHOD_DOC_STRING_TRIPLE_SINGLE_QUOTES = """
class Bar:
    def __init__(self, x):
        ''' Single quotes?! '''
        self.x = x
    """

    METHOD_DOC_STRING_HASH = """
class Bar:
    def __init__(self, x):
        # Hash mon?
        self.x = x
    """

    @pytest.mark.parametrize(
        "doc_string",
        (
            CLASS_DOC_STRING_TRIPLE_DOUBLE_QUOTES,
            FUNC_DOC_STRING_TRIPLE_DOUBLE_QUOTES,
            METHOD_DOC_STRING_TRIPLE_DOUBLE_QUOTES,
        ),
    )
    def test_correct_docstring(self, doc_string):
        errors = results(doc_string)
        assert errors == set()

    @pytest.mark.parametrize("doc_string", (CLASS_DOC_STRING_TRIPLE_SINGLE_QUOTES, CLASS_DOC_STRING_HASH))
    def test_incorrect_docstring_class(self, doc_string):
        errors = results(doc_string)
        assert errors == {"3:4: ROU100 Triple double quotes not used for docstring"}

    @pytest.mark.parametrize("doc_string", (FUNC_DOC_STRING_TRIPLE_SINGLE_QUOTES, FUNC_DOC_STRING_HASH))
    def test_incorrect_docstring_function(self, doc_string):
        errors = results(doc_string)
        assert errors == {"3:4: ROU100 Triple double quotes not used for docstring"}

    @pytest.mark.parametrize("doc_string", (METHOD_DOC_STRING_TRIPLE_SINGLE_QUOTES, METHOD_DOC_STRING_HASH))
    def test_incorrect_docstring_method(self, doc_string):
        errors = results(doc_string)
        assert errors == {"4:8: ROU100 Triple double quotes not used for docstring"}


class TestROU101:
    def test_correct_no_import_from_tests(self):
        result = results("from foo.bar import baz")
        assert result == set()

    def test_incorrect_import_from_tests(self):
        result = results("from foo.tests import bar")
        assert result == {"1:0: ROU101 Import from a tests directory"}
