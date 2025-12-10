# Pip imports
import pytest

# Internal imports
from tests.helpers import results


class TestROU111:
    FEATURE_FLAG_CREATE = """from feature_config.models import FeatureFlag
FeatureFlag.objects.create(company=company, feature_flag=flag)
"""  # noqa ROU102

    FEATURE_FLAG_CREATE_MULTILINE = """from feature_config.models import FeatureFlag
FeatureFlag.objects.create(
    company=company, feature_flag=flag
)
"""  # noqa ROU102

    FEATURE_FLAG_GET_OR_CREATE = """from feature_config.models import FeatureFlag
def method():
    FeatureFlag.objects.get_or_create(company=company, feature_flag=flag)
"""  # noqa ROU102

    FEATURE_FLAG_WITH_COMMENT = """from feature_config.models import FeatureFlag
FeatureFlag.objects.create(  {comment}
    company=company, feature_flag=flag
)
"""  # noqa ROU102

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
