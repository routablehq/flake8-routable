# Internal imports
from tests.helpers import results


class TestROU109:
    ADD_MIGRATION = """class Migration(migrations.Migration):
        dependencies = []
        operations = [
            migrations.AddField(
                model_name="model_one",
                name="swift_charge_option",
                field=models.TextField(blank=True, null=True),
            )
        ]"""

    RENAME_MIGRATION = """class Migration(migrations.Migration):
        dependencies = []
        operations = [
            migrations.RenameField(
                model_name="model_one",
                old="field_one",
                new="field_two",
            )
        ]"""

    def test_correct_no_import_from_tests(self):
        errors = results(self.ADD_MIGRATION)
        assert errors == set()

    def test_incorrect_import_from_tests(self):
        errors = results(self.RENAME_MIGRATION)
        assert errors == {"4:12: ROU109 Disallow rename migrations"}
