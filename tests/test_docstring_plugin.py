import ast
import io
import tokenize

from flake8_routable import ROU100, ROU101, Plugin

CLASS_DOCSTRING_TRIPLE_DOUBLE_QUOTES = (
    "class Foo:\n"
    '    """ What a lovely docstring with lots of things to be talking about"""\n'
    "    pass\n"
)

CLASS_DOCSTRING_TRIPLE_SINGLE_QUOTES = (
    "class Foo:\n"
    "    ''' Single triple quotes for a docstring explaining things? Oh no. '''\n"
    "    pass\n"
)

CLASS_DOCSTRING_HASH = (
    "class Foo:\n"
    "    # Hash mon? Not as a docstring, try again with triple double quotes\n"
    "    pass\n"
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

METHOD_DOCSTRING_TRIPLE_DOUBLE_QUOTES = (
    "class Bar:\n"
    "   def __init__(self, x):\n"
    '       """ What a lovely docstring """\n'
    "       self.x = x\n"
)

METHOD_DOCSTRING_TRIPLE_SINGLE_QUOTES = (
    "class Bar:\n"
    "    def __init__(self, x):\n"
    "        ''' Single quotes?! '''\n"
    "        self.x = x\n"
)

METHOD_DOCSTRING_HASH = (
    "class Bar:\n"
    "    def __init__(self, x):\n"
    "        # Hash mon?\n"
    "        self.x = x\n"
)

MULTI_LINE_FUNC_DOCSTRING_TRIPLE_SINGLE_QUOTES = (
    "def foo(\n"
    "    one_really_long_argument,\n"
    "    another_really_long_argument\n"
    "):\n"
    "    ''' Single quotes?! '''\n"
    "    return x + y\n"
)

INVALID_MULTI_LINE_STRING = (
    "def foo(x, y):\n"
    "\n"
    '    copy = """This is the text\n'
    "    that is spanning multiple lines,\n"
    '    now good bye."""\n'
    "\n"
    '    return f"{x} {y} {copy}"\n'
)

VALID_MULTI_LINE_STRING = (
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

IGNORE_MULTI_LINE_DOCSTRING = (
    "def foo(x, y):\n"
    '    """\n'
    "    I am a docstring,\n"
    "    leave me alone!\n"
    '    """\n'
    "    return x + y\n"
)

IGNORE_MULTI_LINE_COMMENT = (
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

IGNORE_MULTI_LINE_COMMENT_START = '"""hello there,\nhi"""\n'


class PluginTester:
    ERROR_CODES = tuple()

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

        errors = []
        for error in Plugin(tree, tokens).run():
            if error[2] in self.ERROR_CODES:
                errors.append(error)

        return errors


class DocStringTesterBase:
    ERROR_CODES = (ROU100,)

    def test_correct_docstring_single_line_triple_double_quotes(self):
        raise NotImplementedError()

    def test_incorrect_docstring_triple_single_quotes(self):
        raise NotImplementedError()

    def test_incorrect_docstring_hash(self):
        raise NotImplementedError()


class TestMultiLineStrings(PluginTester):
    """Test for multi-line strings being defined correctly."""

    ERROR_CODES = (ROU101,)

    def test_ignore_docstring(self):
        errors = self.get_plugin_errors(IGNORE_MULTI_LINE_DOCSTRING)
        assert len(errors) == 0

    def test_correct_multi_line_string(self):
        errors = self.get_plugin_errors(VALID_MULTI_LINE_STRING)
        assert len(errors) == 0

    def test_incorrect_multi_line_string(self):
        errors = self.get_plugin_errors(INVALID_MULTI_LINE_STRING)
        assert len(errors) == 1
        assert errors[0][0] == 3  # error line no
        assert errors[0][2] == ROU101

    def test_ignore_multi_line_comment(self):
        errors = self.get_plugin_errors(IGNORE_MULTI_LINE_COMMENT)
        assert len(errors) == 0

    def test_multiline_comment_start(self):
        errors = self.get_plugin_errors(IGNORE_MULTI_LINE_COMMENT_START)
        assert len(errors) == 0


class TestClassDocStrings(DocStringTesterBase, PluginTester):
    """Test for triple-double-quotes on class docstrings."""

    def test_correct_docstring_single_line_triple_double_quotes(self):
        errors = self.get_plugin_errors(CLASS_DOCSTRING_TRIPLE_DOUBLE_QUOTES)
        assert len(errors) == 0

    def test_incorrect_docstring_triple_single_quotes(self):
        errors = self.get_plugin_errors(CLASS_DOCSTRING_TRIPLE_SINGLE_QUOTES)

        assert len(errors) == 1
        assert errors[0][0] == 2  # error line no
        assert errors[0][2] == ROU100

    def test_incorrect_docstring_hash(self):
        errors = self.get_plugin_errors(CLASS_DOCSTRING_HASH)

        assert len(errors) == 1
        assert errors[0][0] == 2  # error line no
        assert errors[0][2] == ROU100


class TestFuncDocStrings(DocStringTesterBase, PluginTester):
    """Test for triple-double-quotes on class docstrings."""

    def test_correct_docstring_single_line_triple_double_quotes(self):
        errors = self.get_plugin_errors(FUNC_DOCSTRING_TRIPLE_DOUBLE_QUOTES)
        assert len(errors) == 0

    def test_incorrect_docstring_triple_single_quotes(self):
        errors = self.get_plugin_errors(FUNC_DOCSTRING_TRIPLE_SINGLE_QUOTES)

        assert len(errors) == 1
        assert errors[0][0] == 2  # error line no
        assert errors[0][2] == ROU100

    def test_incorrect_docstring_hash(self):
        errors = self.get_plugin_errors(FUNC_DOCSTRING_HASH)

        assert len(errors) == 1
        assert errors[0][0] == 2  # error line no
        assert errors[0][2] == ROU100

    def test_inline_hash_ignore(self):
        errors = self.get_plugin_errors(FUNC_IGNORE_INLINE_HASH)
        assert len(errors) == 0

    def test_multi_line_func_docstring(self):
        errors = self.get_plugin_errors(MULTI_LINE_FUNC_DOCSTRING_TRIPLE_SINGLE_QUOTES)

        assert len(errors) == 1
        assert errors[0][0] == 5  # error line no
        assert errors[0][2] == ROU100


class TestMethodDocStrings(DocStringTesterBase, PluginTester):
    """Test for triple-double-quotes on class docstrings."""

    def test_correct_docstring_single_line_triple_double_quotes(self):
        errors = self.get_plugin_errors(METHOD_DOCSTRING_TRIPLE_DOUBLE_QUOTES)
        assert len(errors) == 0

    def test_incorrect_docstring_triple_single_quotes(self):
        errors = self.get_plugin_errors(METHOD_DOCSTRING_TRIPLE_SINGLE_QUOTES)

        assert len(errors) == 1
        assert errors[0][0] == 3  # error line no
        assert errors[0][2] == ROU100

    def test_incorrect_docstring_hash(self):
        errors = self.get_plugin_errors(METHOD_DOCSTRING_HASH)

        assert len(errors) == 1
        assert errors[0][0] == 3  # error line no
        assert errors[0][2] == ROU100
