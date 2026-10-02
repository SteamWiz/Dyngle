from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestFixDataOutputOperator(DyngleTestCase):

    def test_newline_on_step_elements(self):
        y = {
            "dyngle": {
                "expressions": {"v": "'x\\n'"},
                "operations": {"a": ["{{v}}"]},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["x"])

    def test_newline_on_outputs(self):
        y = {
            "dyngle": {
                "operations": {"a": ['echo "x" => b', "echo {{b}}y => c"]},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        # Both echoes capture output, so stdout trap should be empty
        self.assertEqual(t.captured, "")
