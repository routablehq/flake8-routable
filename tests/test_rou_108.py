# Internal imports
from tests.helpers import results


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
