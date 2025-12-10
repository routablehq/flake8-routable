# Pip imports
import pytest

# Internal imports
from tests.helpers import results


def create_constant_string(keys, groups=1, tabs=0):
    return "\n\n".join(["\n".join([f"{' '*4*tabs}{key}{i}=None" for key in keys]) for i in range(groups)])


def create_constants_class(keys, groups=1):
    return f"class Thing:\n{create_constant_string(keys, groups=groups, tabs=1)}"


def create_constants_function(keys, groups=1):
    return f"def my_func():\n{create_constant_string(keys, groups=groups, tabs=1)}"


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
