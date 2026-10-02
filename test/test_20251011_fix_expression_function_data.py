from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestFixExpressionFunctionData(DyngleTestCase):

    def test_access_by_data(self):
        y = {
            "dyngle": {
                "constants": {"k": "o"},
                "expressions": {"a": '"f" + k', "b": 'a(data) + "o"'},
                "operations": {"n": ["{{b}}"]},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "n", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["foo"])

    def test_expression_called_with_no_args_uses_current_context(self):
        y = {
            "dyngle": {
                "constants": {"k": "o"},
                "expressions": {"a": '"f" + k', "b": 'a() + "o"'},
                "operations": {"n": ["{{b}}"]},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "n", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["foo"])
