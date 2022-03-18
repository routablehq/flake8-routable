import ast
import io
import tokenize

import pytest

from flake8_routable import ROU100, Plugin

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


class DocStringTesterBaseClass:
    def get_plugin_errors(self, file_str):
        """
        With a string representing a file...
            1. build an AST,
            2. tokenize,
            3. run the flake8 docstring format plugin, and
            4. return any errors.
        """
        tree = ast.parse(file_str)
        tokens = list(tokenize.generate_tokens(io.StringIO(file_str).readline))

        p = Plugin(tree, tokens)
        return list(p.run())

    def test_correct_docstring_single_line_triple_double_quotes(self):
        raise NotImplementedError()

    def test_incorrect_docstring_triple_single_quotes(self):
        raise NotImplementedError()

    def test_incorrect_docstring_hash(self):
        raise NotImplementedError()


class TestClassDocStrings(DocStringTesterBaseClass):
    """Test for triple-double-quotes on class doc strings."""

    def test_correct_docstring_single_line_triple_double_quotes(self):
        errors = self.get_plugin_errors(CLASS_DOC_STRING_TRIPLE_DOUBLE_QUOTES)
        assert len(errors) == 0

    def test_incorrect_docstring_triple_single_quotes(self):
        errors = self.get_plugin_errors(CLASS_DOC_STRING_TRIPLE_SINGLE_QUOTES)

        assert len(errors) == 1
        assert errors[0][0] == 3  # error line no
        assert errors[0][2] == ROU100

    def test_incorrect_docstring_hash(self):
        errors = self.get_plugin_errors(CLASS_DOC_STRING_HASH)

        assert len(errors) == 1
        assert errors[0][0] == 3  # error line no
        assert errors[0][2] == ROU100


class TestFuncDocStrings(DocStringTesterBaseClass):
    """Test for triple-double-quotes on class doc strings."""

    def test_correct_docstring_single_line_triple_double_quotes(self):
        errors = self.get_plugin_errors(FUNC_DOC_STRING_TRIPLE_DOUBLE_QUOTES)
        assert len(errors) == 0

    def test_incorrect_docstring_triple_single_quotes(self):
        errors = self.get_plugin_errors(FUNC_DOC_STRING_TRIPLE_SINGLE_QUOTES)

        assert len(errors) == 1
        assert errors[0][0] == 3  # error line no
        assert errors[0][2] == ROU100

    def test_incorrect_docstring_hash(self):
        errors = self.get_plugin_errors(FUNC_DOC_STRING_HASH)

        assert len(errors) == 1
        assert errors[0][0] == 3  # error line no
        assert errors[0][2] == ROU100


class TestMethodDocStrings(DocStringTesterBaseClass):
    """Test for triple-double-quotes on class doc strings."""

    def test_correct_docstring_single_line_triple_double_quotes(self):
        errors = self.get_plugin_errors(METHOD_DOC_STRING_TRIPLE_DOUBLE_QUOTES)
        assert len(errors) == 0

    def test_incorrect_docstring_triple_single_quotes(self):
        errors = self.get_plugin_errors(METHOD_DOC_STRING_TRIPLE_SINGLE_QUOTES)

        assert len(errors) == 1
        assert errors[0][0] == 4  # error line no
        assert errors[0][2] == ROU100

    def test_incorrect_docstring_hash(self):
        errors = self.get_plugin_errors(METHOD_DOC_STRING_HASH)

        assert len(errors) == 1
        assert errors[0][0] == 4  # error line no
        assert errors[0][2] == ROU100
