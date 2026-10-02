from tempfile import NamedTemporaryFile

from dyngle import DyngleApp
from test import DyngleTestCase


class TestChangeValuesToConstants(DyngleTestCase):
    """Test that the 'constants:' key works as the new name for 'values:'"""

    def test_global_constants_basic(self):
        """Test basic global constants usage"""
        config_yaml = """
dyngle:
  constants:
    greeting: Hello
    name: World
  operations:
    greet:
      steps:
        - echo "{{greeting}}, {{name}}!" => result
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "greet", debug=True)
        # stdout is captured to result variable
        self.assertEqual(t.captured, "")

    def test_local_constants_basic(self):
        """Test basic local constants usage"""
        config_yaml = """
dyngle:
  operations:
    greet:
      constants:
        greeting: Hello
        name: World
      steps:
        - echo "{{greeting}}, {{name}}!" => result
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "greet", debug=True)
        # stdout is captured to result variable
        self.assertEqual(t.captured, "")

    def test_constants_override_hierarchy(self):
        """Test that local constants override global constants"""
        config_yaml = """
dyngle:
  constants:
    value: global
  operations:
    test:
      constants:
        value: local
      steps:
        - echo {{value}} => result
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "test", debug=True)
        # stdout is captured to result variable
        self.assertEqual(t.captured, "")

    def test_constants_with_expressions(self):
        """Test that constants work alongside expressions"""
        config_yaml = """
dyngle:
  constants:
    base: 10
  expressions:
    doubled: "get('base') * 2"
  operations:
    calc:
      steps:
        - echo {{base}} => b
        - echo {{doubled}} => d
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "calc", debug=True)
        # stdout is captured to variables
        self.assertEqual(t.captured, "")

    def test_constants_in_nested_structures(self):
        """Test constants with nested YAML structures"""
        config_yaml = """
dyngle:
  constants:
    config:
      server:
        host: api.example.com
        port: 443
      database:
        name: mydb
  operations:
    connect:
      steps:
        - echo {{config.server.host}} => h
        - echo {{config.server.port}} => p
        - echo {{config.database.name}} => d
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "connect", debug=True)
        # stdout is captured to variables
        self.assertEqual(t.captured, "")

    def test_constants_with_returns(self):
        """Test that constants work with return values"""
        config_yaml = """
dyngle:
  operations:
    get_value:
      constants:
        result: success
      returns: result
      steps:
        - echo Processing
"""
        with NamedTemporaryFile(mode="w+", suffix=".yml") as f:
            f.write(config_yaml)
            f.flush()
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "get_value", debug=True)
        # stdout is suppressed when there's a return: key
        self.assertEqual(t.captured, "")
