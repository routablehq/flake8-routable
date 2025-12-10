# Internal imports
from tests.helpers import results


class TestROU101:
    def test_correct_no_import_from_tests(self):
        errors = results("from foo.bar import baz")
        assert errors == set()

    def test_incorrect_import_from_tests(self):
        errors = results("from foo.tests import bar")
        assert errors == {"1:0: ROU101 Import from a tests directory"}
