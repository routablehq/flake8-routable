# Pip imports
import pytest

# Internal imports
from tests.helpers import results


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
