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
    "    field_b = models.BooleanField(db_default=True, default=False)\n"
    "    field_c = ChoiceField(choices=FieldTypes, db_default=True, default=FieldTypes.A)\n"
    "    field_d = models.JSONField(db_default=True, default=list)\n"
    "    field_e = models.JSONField(db_default=True, default=dict)\n"
    "    field_f = models.DateTimeField(db_default=True, default=timezone.now)"
    ""
)


class TestROU114:

    def test_db_default_no_mismatch(self):
        errors = results(FILE_WITH_DEFAULTS)
        assert errors == set()

    def test_db_default_mismatch(self):
        errors = results(FILE_WITH_MISSING_DEFAULTS)
        assert errors == {
            "5:21: ROU115 Field default and db_default do not match",
            "6:14: ROU115 Field default and db_default do not match",
            "7:21: ROU115 Field default and db_default do not match",
            "8:21: ROU115 Field default and db_default do not match",
            "9:21: ROU115 Field default and db_default do not match",
        }
