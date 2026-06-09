# Internal imports
from tests.helpers import results


class TestROU118:
    ADD_MIGRATION = """class Migration(migrations.Migration):
        dependencies = []
        operations = [
            migrations.AddField(
                model_name="model_one",
                name="swift_charge_option",
                field=models.TextField(blank=True, null=True),
            )
        ]"""

    REMOVE_MIGRATION = """class Migration(migrations.Migration):
        dependencies = []
        operations = [
            migrations.RemoveField(
                model_name="model_one",
                name="field_one",
            )
        ]"""

    def test_correct_no_remove_field(self):
        errors = results(self.ADD_MIGRATION)
        assert errors == set()

    def test_incorrect_remove_field(self):
        errors = results(self.REMOVE_MIGRATION)
        assert errors == {"4:23: ROU118 No migrations.RemoveField"}
