from tempfile import NamedTemporaryFile

from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase
from wizlib.config_handler import ConfigHandler


class TestOperationsCallOperationsAggregate(DyngleTestCase):

    def test_execute_single_task(self):
        config_yaml = """
dyngle:
  operations:
    a:
      constants:
        result: x
      returns: result
      steps:
        - echo b
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        # stdout is suppressed when there's no => operator and return: is set
        self.assertEqual(t.captured, "")

    def test_op_calls_op(self):
        config_yaml = """
dyngle:
  operations:
    a:
      - echo b
    c:
      constants:
        result: x
      returns: result
      steps:
        - sub: a
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "c", debug=True)
        # stdout is suppressed when parent has return: (inherited by sub-op)
        self.assertEqual(t.captured, "")

    def test_invalid_dict_step(self):
        config_yaml = """
dyngle:
  operations:
    c:
      - x: a
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.assertRaises(
                DyngleError
            ):
                DyngleApp.start("--config", f.name, "run", "c", debug=True)

    def test_unknown_op_in_sub(self):
        config_yaml = """
dyngle:
  operations:
    a:
      - echo b
    c:
      - sub: x
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.assertRaises(
                DyngleError
            ):
                DyngleApp.start("--config", f.name, "run", "c", debug=True)

    def test_op_without_steps(self):
        # Test that an operation can have constants but no steps
        # and that a parent can use its own declared constants
        config_yaml = """
dyngle:
  operations:
    a:
      constants:
        x: f
    c:
      constants:
        x: f
      steps:
        - sub: a
        - echo {{x}} => result
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "c", debug=True)
        # stdout is captured to result variable
        self.assertEqual(t.captured, "")
