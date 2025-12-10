# Internal imports
from tests.helpers import results


FILE_WITH_DEFAULTS = (
    "class NewModel(BaseModel):\n"
    "    id = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)\n"
    '    company = models.ForeignKey("entity.Company", on_delete=models.deletion.CASCADE)\n'
    "    field_a = ChoiceField(choices=FieldTypes, null=True)\n"
    "    field_b = models.BooleanField(db_default=False, default=False)\n"
    "    field_c = ChoiceField(choices=FieldTypes, db_default=FieldTypes.A, default=FieldTypes.A)\n"
    "    field_d = models.JSONField(db_default=[], default=list)\n"
    "    field_e = models.JSONField(db_default={}, default=dict)\n"
    "    field_f = models.DateTimeField(db_default=Now(), default=timezone.now)"
    ""
)

FILE_WITH_MISSING_DEFAULTS = (
    "class NewModel(BaseModel):\n"
    "    id = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)\n"
    '    company = models.ForeignKey("entity.Company", on_delete=models.deletion.CASCADE)\n'
    "    field_a = ChoiceField(choices=FieldTypes, null=True)\n"
    "    field_b = models.BooleanField(default=False)\n"
    "    field_c = ChoiceField(choices=FieldTypes, default=FieldTypes.A)\n"
    "    field_d = models.JSONField(default=list)\n"
    "    field_e = models.JSONField(default=dict)\n"
    "    field_f = models.DateTimeField(default=timezone.now)"
    ""
)


class TestROU114:

    def test_no_missing_db_default(self):
        errors = results(FILE_WITH_DEFAULTS)
        assert errors == set()

    def test_missing_db_default(self):
        errors = results(FILE_WITH_MISSING_DEFAULTS)
        assert errors == {
            "5:21: ROU114 Field default exists but db_default does not",
            "6:14: ROU114 Field default exists but db_default does not",
            "7:21: ROU114 Field default exists but db_default does not",
            "8:21: ROU114 Field default exists but db_default does not",
            "9:21: ROU114 Field default exists but db_default does not",
        }

    def test_missing_db_default_in_excluded_files(self):
        errors = results(FILE_WITH_MISSING_DEFAULTS, "/tests/test.py")
        assert errors == set()
