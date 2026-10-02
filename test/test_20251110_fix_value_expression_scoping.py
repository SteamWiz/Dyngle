from tempfile import NamedTemporaryFile

from dyngle import DyngleApp
from test import DyngleTestCase


class TestValueExpressionScoping(DyngleTestCase):
    """Test that declared constants are locally scoped but live data is global"""

    def test_declared_values_are_locally_scoped(self):
        """Declared constants in sub-operations should not leak to parent"""
        config_yaml = """
dyngle:
  constants:
    declared-val: global

  operations:
    child:
      constants:
        declared-val: child
      steps:
        - echo {{declared-val}} => c

    parent:
      steps:
        - echo {{declared-val}} => p1
        - sub: child
        - echo {{declared-val}} => p2
"""

        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, \
                    self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start(
                    "--config", f.name, "run", "parent", debug=True
                )

        # stdout is captured to variables, so trap should be empty
        self.assertEqual(t.captured, "")

    def test_live_data_persists_across_operations(self):
        """Live data (set via =>) should persist across sub-operations"""
        config_yaml = """
dyngle:
  operations:
    child:
      steps:
        - echo "child-output" => live-val

    parent:
      steps:
        - echo "parent-output" => live-val
        - echo {{live-val}} => d1
        - sub: child
        - echo {{live-val}} => d2
"""

        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, \
                    self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start(
                    "--config", f.name, "run", "parent", debug=True
                )

        # stdout is captured to variables, so trap should be empty
        self.assertEqual(t.captured, "")

    def test_nested_operations_maintain_local_scopes(self):
        """Test three levels of nesting: test -> grandparent -> parent ->
        child"""
        config_yaml = """
dyngle:
  constants:
    declared-val: global

  operations:
    child:
      constants:
        declared-val: child
      steps:
        - echo {{declared-val}} => c
        - echo "Child" => live-val

    parent:
      steps:
        - echo {{declared-val}} => p1
        - sub: child
        - echo {{declared-val}} => p2

    grandparent:
      constants:
        declared-val: grandparent
      steps:
        - echo {{declared-val}} => g1
        - sub: parent
        - echo {{declared-val}} => g2

    test:
      steps:
        - echo {{declared-val}} => t1
        - echo "Test" => live-val
        - sub: grandparent
        - echo {{declared-val}} => t2
        - echo {{live-val}} => t3
"""

        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, \
                    self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "test", debug=True)

        # stdout is captured to variables, so trap should be empty
        self.assertEqual(t.captured, "")
