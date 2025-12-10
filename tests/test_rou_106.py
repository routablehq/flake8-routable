# Pip imports
import pytest

# Internal imports
from tests.helpers import results


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
