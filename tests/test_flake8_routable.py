# Python imports
import ast
import io
import tokenize

# Pip imports
import pytest

# Internal imports
from flake8_routable import Plugin, Visitor


def results(s):
    return {
        "{}:{}: {}".format(*r)
        for r in Plugin(ast.parse(s), list(tokenize.generate_tokens(io.StringIO(s).readline))).run()
    }


def create_constant_string(keys, groups=1, tabs=0):
    return "\n\n".join(["\n".join([f"{' '*4*tabs}{key}{i}=None" for key in keys]) for i in range(groups)])


def create_constants_class(keys, groups=1):
    return f"class Thing:\n{create_constant_string(keys, groups=groups, tabs=1)}"


def create_constants_function(keys, groups=1):
    return f"def my_func():\n{create_constant_string(keys, groups=groups, tabs=1)}"


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


class TestROU103:
    COLLECTION_CORRECT_ORDER = (
        ("1", "2"),
        ("'bar'", "'baz'", "'foo'"),
        ("bar", "baz", "foo"),
        ("A.B", "B.A"),
        ("f'a {b}'", "f'{b} a'"),
        ("a.b()", "b.a()"),
        ("a['b']", "b['a']"),
        ("3", "'a'", "b", "C.D", "E.F.G", "h.i()", "f'j'", "k['l']"),
        ("foo", "'foo'"),
        ("'foo'", "foo"),
        ("(a, 'b')", "(b, 'a')"),
    )

    COLLECTION_INCORRECT_ORDER = (
        ("2", "1"),
        ("'foo'", "'bar'", "'baz'"),
        ("foo", "bar", "baz"),
        ("B.A", "A.B"),
        ("f'b {a}'", "f'{a} b'"),
        ("b.a()", "a.b()"),
        ("b['a']", "a['b']"),
        ("('b', a)", "('a', b)"),
    )

    @staticmethod
    def create_dict_string(keys):
        dict_entries = ", ".join([f"{key}: None" for key in keys])
        return f"{{{dict_entries}}}"

    @staticmethod
    def create_set_string(keys):
        set_entries = ", ".join(keys)
        return f"{{{set_entries}}}"

    @pytest.mark.parametrize("correct_order", COLLECTION_CORRECT_ORDER)
    def test_dict_correct_order(self, correct_order):
        dict_string = self.create_dict_string(correct_order)
        error = results(dict_string)
        assert error == set()

    @pytest.mark.parametrize("incorrect_order", COLLECTION_INCORRECT_ORDER)
    def test_dict_incorrect_order(self, incorrect_order):
        dict_string = self.create_dict_string(incorrect_order)
        error = results(dict_string)
        assert error == {"1:0: ROU103 Object does not have attributes in order"}

    @pytest.mark.parametrize("correct_order", COLLECTION_CORRECT_ORDER)
    def test_set_correct_order(self, correct_order):
        dict_string = self.create_set_string(correct_order)
        error = results(dict_string)
        assert error == set()

    @pytest.mark.parametrize("incorrect_order", COLLECTION_INCORRECT_ORDER)
    def test_set_incorrect_order(self, incorrect_order):
        dict_string = self.create_set_string(incorrect_order)
        error = results(dict_string)
        assert error == {"1:0: ROU103 Object does not have attributes in order"}


class TestROU104:
    BLANK_LINE_AFTER_COMMENT = "# Setup\n\nUser = get_user_model()\n"
    BLANK_LINES_AFTER_REVIEW_TIMESTAMP = "# 2020-04-06 - Needs review\n\n\nX = 4"
    BLANK_LINES_AFTER_SECTION = "# -------\n# Tests\n# -------\n\n\nX = 4"
    BLANK_LINES_AFTER_SUBSECTION = "# =======\n# Tests\n# =======\n\n\nX = 4"
    BLANK_LINES_BEFORE_DEDENT_SECTION = (
        "class AffiliateModelSerializer(serializers.ModelSerializer):\n"
        '    """Affiliate model serializer."""\n\n'
        "    # Private attributes\n\n"
        "    # Fields\n\n"
        "    # Nested classes\n\n"
        "    class Meta:\n"
        "        model = Affiliate\n\n"
        "        fields = [\n"
        '            "generic_url",\n'
        '            "logo",\n'
        '            "name",\n'
        '            "primary_color",\n'
        "        ]\n\n"
        "    # Methods\n\n\n"
        "# --------------------\n"
        "# Main model serializers\n"
        "# --------------------\n"
    )
    BLANK_LINES_BEFORE_DEDENT_STATEMENT = (
        "class FeatureFlagModelSerializer(serializers.ModelSerializer):\n"
        '    """FeatureFlag model serializer."""\n\n'
        "    class Meta:\n"
        "        model = FeatureFlag\n"
        '        fields = ["feature_flag"]\n\n'
        "    # Special method overrides\n\n"
        "    # Private methods\n\n"
        "    # Class methods\n\n"
        "    # Properties\n\n"
        "    # Overrides\n\n"
        "    # Validation\n\n"
        "    # Methods\n\n\n"
        "@spicy_decorator\n"
        "class FeatureSettingSerializer(NoCreateUpdateMixin, serializers.Serializer):\n"
        "    pass\n"
    )

    def test_incorrect_blank_lines_after_comment(self):
        errors = results("# Setup\n\n\nUser = get_user_model()\n")
        assert errors == {"3:0: ROU104 Multiple blank lines are not allowed after a non-section comment"}

    @pytest.mark.parametrize(
        "blank_lines_string",
        (
            BLANK_LINE_AFTER_COMMENT,
            BLANK_LINES_AFTER_SECTION,
            BLANK_LINES_AFTER_SUBSECTION,
            BLANK_LINES_AFTER_REVIEW_TIMESTAMP,
            BLANK_LINES_BEFORE_DEDENT_SECTION,
            BLANK_LINES_BEFORE_DEDENT_STATEMENT,
        ),
    )
    def test_correct_blank_lines(self, blank_lines_string):
        errors = results(blank_lines_string)
        assert errors == set()


class TestROU105:
    CONSTANTS_CORRECT_ORDER = ("A", "B", "C")

    CONSTANTS_INCORRECT_ORDER = ("B", "C", "A")

    @pytest.mark.parametrize(
        "generator_function", (create_constant_string, create_constants_class, create_constants_function)
    )
    @pytest.mark.parametrize("groups", (1, 2, 3))
    def test_constants_correct_order(self, generator_function, groups):
        constants_string = generator_function(self.CONSTANTS_CORRECT_ORDER, groups=groups)
        error = results(constants_string)
        assert error == set()

    @pytest.mark.parametrize("groups", (1, 2, 3))
    def test_constants_class_correct_order(self, groups):
        constants_string = create_constants_class(self.CONSTANTS_CORRECT_ORDER, groups)
        error = results(constants_string)
        assert error == set()

    @pytest.mark.parametrize(
        ("generator_function", "line_info"),
        ((create_constant_string, "1:0"), (create_constants_class, "2:4"), (create_constants_function, "2:4")),
    )
    def test_constants_incorrect_order(self, generator_function, line_info):
        constants_string = generator_function(self.CONSTANTS_INCORRECT_ORDER)
        error = results(constants_string)
        assert error == {f"{line_info}: ROU105 Constants are not in order"}

    def test_constants_incorrect_order_second_group(self):
        constants_group_correct = create_constant_string(self.CONSTANTS_CORRECT_ORDER)
        constants_group_incorrect = create_constant_string(self.CONSTANTS_INCORRECT_ORDER)
        constants_string = f"{constants_group_correct}\n\n{constants_group_incorrect}"
        error = results(constants_string)
        assert error == {"5:0: ROU105 Constants are not in order"}

    def test_constants_incorrect_order_multiple_groups(self):
        constants_string = create_constant_string(self.CONSTANTS_INCORRECT_ORDER, groups=2)
        error = results(constants_string)
        assert error == {"1:0: ROU105 Constants are not in order", "5:0: ROU105 Constants are not in order"}

    # ------------
    # Edge Cases
    # ------------

    def test_constants_multi_line_assignment_correct(self):
        constants_string = "\n".join(key + " = (\nNone\n)" for key in self.CONSTANTS_CORRECT_ORDER)
        error = results(constants_string)
        assert error == set()

    def test_constants_multi_line_assignment_incorrect(self):
        constants_string = "\n".join(key + " = (\nNone\n)" for key in self.CONSTANTS_INCORRECT_ORDER)
        error = results(constants_string)
        assert error == {"1:0: ROU105 Constants are not in order"}

    def test_constants_with_underscores_correct(self):
        constants_string = "A_BC=None\nAB_C=None"
        error = results(constants_string)
        assert error == set()

    def test_constants_with_underscores_incorrect(self):
        constants_string = "AB_C=None\nA_BC=None"
        error = results(constants_string)
        assert error == {"1:0: ROU105 Constants are not in order"}


class TestROU106:
    RELATIVE_IMPORT_LEVEL_UP = "from ..constants import FOO"
    RELATIVE_IMPORT_SAME_LEVEL = "from .constants import FOO"

    @pytest.mark.parametrize(
        "rel_import",
        (
            RELATIVE_IMPORT_LEVEL_UP,
            RELATIVE_IMPORT_SAME_LEVEL,
        ),
    )
    def test_relative_import(self, rel_import):
        error = results(rel_import)
        assert error == {"1:0: ROU106 Relative imports are not allowed"}

    def test_absolute_import(self):
        error = results("from utils.constants import BAR")
        assert error == set()


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


class TestROU108:
    def test_non_model_subpackage_import(self):
        error = results("from app.constants.subpackage import ModelA, ModelB")
        assert error == set()

    def test_non_model_named_like_a_model_subpackage_import(self):
        error = results("from app.like_a_model.subpackage import ModelA, ModelB")
        assert error == set()

    def test_model_subpackage_import(self):
        error = results("from app.models.subpackage import ModelA, ModelB")
        assert error == {"1:0: ROU108 Import from model module instead of sub-packages"}

    def test_model_module_import(self):
        error = results("from app.models import Model")
        assert error == set()


class TestROU109:
    ADD_MIGRATION = """class Migration(migrations.Migration):
        dependencies = []
        operations = [
            migrations.AddField(
                model_name="model_one",
                name="swift_charge_option",
                field=models.TextField(blank=True, null=True),
            )
        ]"""

    RENAME_MIGRATION = """class Migration(migrations.Migration):
        dependencies = []
        operations = [
            migrations.RenameField(
                model_name="model_one",
                old="field_one",
                new="field_two",
            )
        ]"""

    def test_correct_no_import_from_tests(self):
        errors = results(self.ADD_MIGRATION)
        assert errors == set()

    def test_incorrect_import_from_tests(self):
        errors = results(self.RENAME_MIGRATION)
        assert errors == {"4:12: ROU109 Disallow rename migrations"}


class TestROU110:
    SAVE_WITH_UPDATE_FIELDS = """from app.models import Model
instance = Model(id="123", name="test")
instance.save(update_fields=["id", "name"])
"""

    SAVE_MULTILINE_WITH_UPDATE_FIELDS_FLAG = """from app.models import Model
instance = Model(id="123", name="test")
instance.save(  # multi-line with update_fields
    update_fields=["id", "name"]
)
"""

    SAVE_WITHOUT_UPDATE_FIELDS = """from app.models import Model
instance = Model(id="123", name="test")
instance.save()
instance.save(using="default")
"""

    SAVE_WITH_COMMENT = """from app.models import Model
instance = Model(id="123", name="test")
instance.save()  {comment}
"""

    def test_save_with_update_fields(self):
        errors = results(self.SAVE_WITH_UPDATE_FIELDS)
        assert errors == set()

    def test_save__multiline_with_update_fields_flag(self):
        errors = results(self.SAVE_MULTILINE_WITH_UPDATE_FIELDS_FLAG)
        assert errors == set()

    def test_save_without_update_fields(self):
        errors = results(self.SAVE_WITHOUT_UPDATE_FIELDS)
        assert errors == {
            "3:0: ROU110 Disallow .save() with no update_fields",
            "4:0: ROU110 Disallow .save() with no update_fields",
        }

    @pytest.mark.parametrize(
        "comment",
        [
            "# TODO: needs fix",
            "# file save",
            "# form save",
            "# ledger save",
            "# new model save",
            "# not a model",
            "# save extension",
            "# serializer save",
        ],
    )
    def test_with_comment(self, comment):
        errors = results(self.SAVE_WITH_COMMENT.format(comment=comment))
        assert errors == set()


class TestROU111:
    FEATURE_FLAG_CREATE = """from feature_config.models import FeatureFlag
FeatureFlag.objects.create(company=company, feature_flag=flag)
"""

    FEATURE_FLAG_CREATE_MULTILINE = """from feature_config.models import FeatureFlag
FeatureFlag.objects.create(
    company=company, feature_flag=flag
)
"""

    FEATURE_FLAG_GET_OR_CREATE = """from feature_config.models import FeatureFlag
def method():
    FeatureFlag.objects.get_or_create(company=company, feature_flag=flag)
"""

    FEATURE_FLAG_WITH_COMMENT = """from feature_config.models import FeatureFlag
FeatureFlag.objects.create(  {comment}
    company=company, feature_flag=flag
)
"""

    def test_feature_flag_create(self):
        errors = results(self.FEATURE_FLAG_CREATE)
        assert errors == {
            "2:0: ROU111 Disallow FeatureFlag creation in code",
        }

    def test_feature_flag_create_multiline(self):
        errors = results(self.FEATURE_FLAG_CREATE_MULTILINE)
        assert errors == {
            "2:0: ROU111 Disallow FeatureFlag creation in code",
        }

    def test_feature_flag_get_or_create(self):
        errors = results(self.FEATURE_FLAG_GET_OR_CREATE)
        assert errors == {
            "3:0: ROU111 Disallow FeatureFlag creation in code",
        }

    @pytest.mark.parametrize(
        "comment",
        [
            "# valid for legacy cross-border work",
            "# valid for management command",
        ],
    )
    def test_with_comment(self, comment):
        errors = results(self.FEATURE_FLAG_WITH_COMMENT.format(comment=comment))
        assert errors == set()

    @pytest.mark.parametrize(
        "comment",
        [
            "# valid for something else",
            " ",
        ],
    )
    def test_with_invalid_comment(self, comment):
        errors = results(self.FEATURE_FLAG_WITH_COMMENT.format(comment=comment))
        assert errors == {
            "2:0: ROU111 Disallow FeatureFlag creation in code",
        }


class TestROU112:
    TASK_DECORATOR_WITH_PARAMS_WITH_ARGS_KWARGS = (
        "\n"
        "@shared_task(autoretry_for=(Exception,), default_retry_delay=20)\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    *args,\n"
        "    **kwargs,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_DECORATOR_WITH_PARAMS_MISSING_ARGS_KWARGS = (
        "\n"
        "@shared_task(autoretry_for=(Exception,), default_retry_delay=20)\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_WITH_TYPES_WITH_PARAMS_WITH_ARGS_KWARGS = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1: str,\n"
        "    field_2: int,\n"
        "    *args,\n"
        "    **kwargs,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_WITH_TYPES_WITH_PARAMS_MISSING_ARGS_KWARGS = (
        "\n" "@shared_task\n" "def task_method(\n" "    field_1: str,\n" "    field_2: int,\n" "):" "    pass\n" "\n"
    )

    TASK_MULTILINE_WITH_ARGS_KWARGS = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    *args,\n"
        "    **kwargs,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_SINGLELINE_WITH_ARGS_KWARGS = (
        "\n" "@shared_task\n" "def task_method(field_1, field_2, *args, **kwargs):\n" "    pass\n" "\n"
    )

    TASK_MULTILINE_MISSING_ARGS = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    **kwargs,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_SINGLELINE_MISSING_ARGS = (
        "\n" "@shared_task\n" "def task_method(field_1, field_2, **kwargs):\n" "    pass\n" "\n"
    )

    TASK_MULTILINE_MISSING_KWARGS = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    *args,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_SINGLELINE_MISSING_KWARGS = (
        "\n" "@shared_task\n" "def task_method(field_1, field_2, *args):\n" "    pass\n" "\n"
    )

    TASK_MULTILINE_MISSING_ARGS_KWARGS = (
        "\n" "@shared_task\n" "def task_method(\n" "    field_1,\n" "    field_2,\n" "):" "    pass\n" "\n"
    )

    TASK_SINGLELINE_MISSING_ARGS_KWARGS = "\n" "@shared_task\n" "def task_method(field_1, field_2):\n" "    pass\n" "\n"

    @pytest.mark.parametrize(
        "code",
        (
            TASK_DECORATOR_WITH_PARAMS_WITH_ARGS_KWARGS,
            TASK_WITH_TYPES_WITH_PARAMS_WITH_ARGS_KWARGS,
            TASK_MULTILINE_WITH_ARGS_KWARGS,
            TASK_SINGLELINE_WITH_ARGS_KWARGS,
        ),
    )
    def test_correct_signature(self, code):
        errors = results(code)
        assert errors == set()

    @pytest.mark.parametrize(
        ("code", "location"),
        (
            (TASK_DECORATOR_WITH_PARAMS_MISSING_ARGS_KWARGS, "6:1"),
            (TASK_WITH_TYPES_WITH_PARAMS_MISSING_ARGS_KWARGS, "6:1"),
            (TASK_MULTILINE_MISSING_ARGS, "7:1"),
            (TASK_SINGLELINE_MISSING_ARGS, "3:43"),
            (TASK_MULTILINE_MISSING_KWARGS, "7:1"),
            (TASK_SINGLELINE_MISSING_KWARGS, "3:40"),
            (TASK_MULTILINE_MISSING_ARGS_KWARGS, "6:1"),
            (TASK_SINGLELINE_MISSING_ARGS_KWARGS, "3:33"),
        ),
    )
    def test_incorrect_signature(self, code, location):
        errors = results(code)
        assert errors == {f"{location}: ROU112 Tasks mush have *args, **kwargs"}


class TestROU113:
    TASK_WITH_OUT_PRIORITY = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    *args,\n"
        "    **kwargs,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_WITH_PRIORITY = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    priority,\n"
        "    *args,\n"
        "    **kwargs,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_WITH_PRIORITY_MISSING_ARGS = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    priority,\n"
        "    **kwargs,\n"
        "):"
        "    pass\n"
        "\n"
    )

    TASK_WITH_PRIORITY_MISSING_KWARGS = (
        "\n"
        "@shared_task\n"
        "def task_method(\n"
        "    field_1,\n"
        "    field_2,\n"
        "    priority,\n"
        "    *args,\n"
        "):"
        "    pass\n"
        "\n"
    )

    @pytest.mark.parametrize(
        "code",
        (TASK_WITH_OUT_PRIORITY,),
    )
    def test_correct_signature(self, code):
        errors = results(code)
        assert errors == set()

    @pytest.mark.parametrize(
        ("code", "error"),
        (
            (TASK_WITH_PRIORITY, {"6:4: ROU113 Tasks can not have priority in the signature"}),
            (
                TASK_WITH_PRIORITY_MISSING_ARGS,
                {
                    "6:4: ROU113 Tasks can not have priority in the signature",
                    "8:1: ROU112 Tasks mush have *args, **kwargs",
                },
            ),
            (
                TASK_WITH_PRIORITY_MISSING_KWARGS,
                {
                    "6:4: ROU113 Tasks can not have priority in the signature",
                    "8:1: ROU112 Tasks mush have *args, **kwargs",
                },
            ),
        ),
    )
    def test_incorrect_signature(self, code, error):
        errors = results(code)
        assert errors == error


class TestROU114:
    def test_prefix_usage(self):
        errors = results("something_mock.called_once_with(test)")
        assert errors == {"1:15: ROU114 prefix .called_ for attributes of mock objects"}

    def test_with_correct_prefix_usage(self):
        errors = results("something_mock.assert_called_once_with(test)")
        assert errors == set()


class TestVisitor:
    def test_parse_to_string_warning(self):
        visitor = Visitor()
        with pytest.warns(UserWarning):
            visitor._parse_to_string(None)
