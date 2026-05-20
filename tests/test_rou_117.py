# Internal imports
from tests.helpers import results


FILE_WITH_ON_COMMIT = (
    "my_task.delay_on_commit(arg1, arg2, kwarg1=kwarg1, kwarg2=kwarg2)\n"
    'my_task.apply_async_on_commit(args=[arg, arg2], kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2})\n'
    'celery.send_task_on_commit("my_task", args=[arg, arg2], kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2})\n'
)

FILE_WITHOUT_ON_COMMIT = (
    "my_task.delay(arg1, arg2, kwarg1=kwarg1, kwarg2=kwarg2)\n"
    'my_task.apply_async(args=[arg, arg2], kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2})\n'
    'celery.send_task("my_task", args=[arg, arg2], kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2})\n'
)

FILE_WITH_ON_COMMIT_MULTILINE = (
    "my_task.delay_on_commit(\n"
    "    arg1,\n"
    "    arg2,\n"
    "    kwarg1=kwarg1,\n"
    "    kwarg2=kwarg2,\n"
    ")\n"
    "my_task.apply_async_on_commit(\n"
    "    args=[arg1, arg2],\n"
    '    kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2},\n'
    "    countdown=5,\n"
    ")\n"
    "celery.send_task_on_commit(\n"
    '    "my_task",\n'
    "    args=[arg1, arg2],\n"
    '    kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2},\n'
    "    countdown=5,\n"
    ")\n"
)

FILE_WITHOUT_ON_COMMIT_MULTILINE = (
    "my_task.delay(\n"
    "    arg1,\n"
    "    arg2,\n"
    "    kwarg1=kwarg1,\n"
    "    kwarg2=kwarg2,\n"
    ")\n"
    "my_task.apply_async(\n"
    "    args=[arg1, arg2],\n"
    '    kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2},\n'
    "    countdown=5,\n"
    ")\n"
    "celery.send_task(\n"
    '    "my_task",\n'
    "    args=[arg1, arg2],\n"
    '    kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2},\n'
    "    countdown=5,\n"
    ")\n"
)

FILE_WITH_ON_COMMIT_ATTRIBUTE_ASSIGNMENT = (
    "my_task_delay_ref = my_task.delay_on_commit\n"
    "my_task_apply_async_ref = some_module.apply_async_on_commit\n"
    "my_send_task_ref = celery.send_task_on_commit\n"
)

FILE_WITHOUT_ON_COMMIT_ATTRIBUTE_ASSIGNMENT = (
    "my_task_delay_ref = my_task.delay\n"
    "my_task_apply_async_ref = some_module.apply_async\n"
    "my_send_task_ref = celery.send_task\n"
)


class TestROU117:

    def test_using_on_commit(self):
        errors = results(FILE_WITH_ON_COMMIT)
        assert errors == set()

    def test_not_using_on_commit(self):
        errors = results(FILE_WITHOUT_ON_COMMIT)
        assert errors == {
            "1:8: ROU117 not using *_on_commit",
            "2:8: ROU117 not using *_on_commit",
            "3:7: ROU117 not using *_on_commit",
        }

    def test_using_on_commit_multiline(self):
        errors = results(FILE_WITH_ON_COMMIT_MULTILINE)
        assert errors == set()

    def test_not_using_on_commit_multiline(self):
        errors = results(FILE_WITHOUT_ON_COMMIT_MULTILINE)
        assert errors == {
            "1:8: ROU117 not using *_on_commit",
            "7:8: ROU117 not using *_on_commit",
            "12:7: ROU117 not using *_on_commit",
        }

    def test_using_on_commit_attribute_assignment(self):
        errors = results(FILE_WITH_ON_COMMIT_ATTRIBUTE_ASSIGNMENT)
        assert errors == set()

    def test_not_using_on_commit_attribute_assignment(self):
        errors = results(FILE_WITHOUT_ON_COMMIT_ATTRIBUTE_ASSIGNMENT)
        assert errors == {
            "1:28: ROU117 not using *_on_commit",
            "2:38: ROU117 not using *_on_commit",
            "3:26: ROU117 not using *_on_commit",
        }
