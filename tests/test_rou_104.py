# Pip imports
import pytest

# Internal imports
from tests.helpers import results


class TestROU104:
    BLANK_LINE_AFTER_COMMENT = "# Setup\n\nUser = get_user_model()\n"
    BLANK_LINES_AFTER_SECTION = "# -------\n# Tests\n# -------\n\n\nX = 4"
    BLANK_LINES_AFTER_SUBSECTION = "# =======\n# Tests\n# =======\n\n\nX = 4"
    BLANK_LINES_BEFORE_DEDENT_SECTION = (
        "class AffiliateModelSerializer(serializers.ModelSerializer):\n"
        '    """Affiliate model serializer."""\n\n'
        "    # Private attributes\n\n"
        "    # Fields\n\n"
        "    # Nested classes\n\n"
        "    class Meta:\n"
        "        model = Affiliate\n\n"
        "        fields = [\n"
        '            "generic_url",\n'
        '            "logo",\n'
        '            "name",\n'
        '            "primary_color",\n'
        "        ]\n\n"
        "    # Methods\n\n\n"
        "# --------------------\n"
        "# Main model serializers\n"
        "# --------------------\n"
    )
    BLANK_LINES_BEFORE_DEDENT_STATEMENT = (
        "class FeatureFlagModelSerializer(serializers.ModelSerializer):\n"
        '    """FeatureFlag model serializer."""\n\n'
        "    class Meta:\n"
        "        model = FeatureFlag\n"
        '        fields = ["feature_flag"]\n\n'
        "    # Special method overrides\n\n"
        "    # Private methods\n\n"
        "    # Class methods\n\n"
        "    # Properties\n\n"
        "    # Overrides\n\n"
        "    # Validation\n\n"
        "    # Methods\n\n\n"
        "@spicy_decorator\n"
        "class FeatureSettingSerializer(NoCreateUpdateMixin, serializers.Serializer):\n"
        "    pass\n"
    )

    def test_incorrect_blank_lines_after_comment(self):
        errors = results("# Setup\n\n\nUser = get_user_model()\n")
        assert errors == {"3:0: ROU104 Multiple blank lines are not allowed after a non-section comment"}

    @pytest.mark.parametrize(
        "blank_lines_string",
        (
            BLANK_LINE_AFTER_COMMENT,
            BLANK_LINES_AFTER_SECTION,
            BLANK_LINES_AFTER_SUBSECTION,
            BLANK_LINES_BEFORE_DEDENT_SECTION,
            BLANK_LINES_BEFORE_DEDENT_STATEMENT,
        ),
    )
    def test_correct_blank_lines(self, blank_lines_string):
        errors = results(blank_lines_string)
        assert errors == set()
