import subprocess
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from yaml import safe_dump

from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.context import Context
from dyngle.model.operation import CommandStep
from test import DyngleTestCase
import dyngle.model.operation

class TestRightAngleOperator(DyngleTestCase):

    def test_parsing(self):
        s = CommandStep(None, Context(), "f")
        self.assertIsNone(s.payload_context_path)
        self.assertIsNone(s.result_key)
        # self.assertEqual(s.command_template, ["f"])

    def test_parsing_error(self):
        with self.assertRaises(DyngleError):
            s = CommandStep(None, Context(), "")

    # def test_subprocess_trap(self):
    #     with self.subprocess_runner_trap() as t:
    #         dyngle.model.operation.run_subprocess(["echo", "hello world"])
    #         dyngle.model.operation.run_subprocess(["echo", "another line"])
    #     # t.stdout.seek(0)
    #     # lines = t.stdout.readlines()
    #     self.assertEqual(t.captured, "hello world")

    def test_preliminary(self):
        # Test that stdout is suppressed when no output operator
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "constants": {"dummy": "x"},
                        "returns": "dummy",
                        "steps": ["echo x"]
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e, self.patch_stream("b: x"):
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        # Stdout is suppressed when there's no => operator and return: is set
        self.assertEqual(t.captured, "")

    def test_assign(self):
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "returns": "b",
                        "steps": ['echo -n "x" => b', "echo {{b}}"]
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        # Second echo has no => so stdout is suppressed with return:
        self.assertEqual(t.captured, "")
