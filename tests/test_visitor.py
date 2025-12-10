# Pip imports
import pytest

# Internal imports
from flake8_routable import Visitor


class TestVisitor:
    def test_parse_to_string_warning(self):
        visitor = Visitor()
        with pytest.warns(UserWarning):
            visitor._parse_to_string(None)
