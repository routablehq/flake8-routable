# Pip imports
import pytest

# Internal imports
from tests.helpers import results


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
