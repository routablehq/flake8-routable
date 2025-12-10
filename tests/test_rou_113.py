# Pip imports
import pytest

# Internal imports
from tests.helpers import results


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
