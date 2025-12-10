# Pip imports
import pytest

# Internal imports
from tests.helpers import results


class TestROU110:
    SAVE_WITH_UPDATE_FIELDS = """from app.models import Model
instance = Model(id="123", name="test")
instance.save(update_fields=["id", "name"])
"""  # noqa ROU102

    SAVE_MULTILINE_WITH_UPDATE_FIELDS_FLAG = """from app.models import Model
instance = Model(id="123", name="test")
instance.save(  # multi-line with update_fields
    update_fields=["id", "name"]
)
"""  # noqa ROU102

    SAVE_WITHOUT_UPDATE_FIELDS = """from app.models import Model
instance = Model(id="123", name="test")
instance.save()
instance.save(using="default")
"""  # noqa ROU102

    SAVE_WITH_COMMENT = """from app.models import Model
instance = Model(id="123", name="test")
instance.save()  {comment}
"""  # noqa ROU102

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
