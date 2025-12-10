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
    "    field_b = models.BooleanField(db_default=False, default=False, null=True)\n"
    "    field_c = ChoiceField(choices=FieldTypes, db_default=FieldTypes.A, default=FieldTypes.A, null=True)\n"
    "    field_d = models.JSONField(db_default=[], default=list, null=True)\n"
    "    field_e = models.JSONField(db_default={}, default=dict, null=True)\n"
    "    field_f = models.DateTimeField(db_default=Now(), default=timezone.now, null=True)"
    ""
)


class TestROU114:

    def test_default_with_no_nulls(self):
        errors = results(FILE_WITH_DEFAULTS)
        assert errors == set()

    def test_default_with_nulls(self):
        errors = results(FILE_WITH_MISSING_DEFAULTS)
        assert errors == {
            "5:21: ROU116 Field has both default and null set",
            "6:14: ROU116 Field has both default and null set",
            "7:21: ROU116 Field has both default and null set",
            "8:21: ROU116 Field has both default and null set",
            "9:21: ROU116 Field has both default and null set",
        }
