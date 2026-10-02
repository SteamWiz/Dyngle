from tempfile import NamedTemporaryFile

from dyngle import DyngleApp
from test import DyngleTestCase


class TestValueResolutionFailureImports(DyngleTestCase):
    """Test that constants from source config are available in imported configs"""

    def test_imported_config_can_access_source_values(self):
        """
        When a source config defines constants and imports another config,
        the imported config's operations should be able to access those constants.

        Reproduces bug where:
        - Source config (value-source.yml) defines `name: Francis`
        - Source config imports target config (value-target.yml)
        - Target config operation tries to use {{name}}
        - Expected: Should resolve to 'Francis'
        - Actual: DyngleError: Invalid expression or data reference 'name'
        """
        # Create the target config (to be imported)
        target_yaml = """
dyngle:
  constants:
    local-value: Amor
  operations:
    doit:
      - echo {{local-value}} => l
      - echo {{name}} => n
"""

        with NamedTemporaryFile(
            mode="w+", suffix=".yml", delete=False
        ) as target_file:
            target_file.write(target_yaml)
            target_file.flush()
            target_file.seek(0)

            # Create the source config that defines constants and imports target
            source_yaml = f"""
dyngle:
  constants:
    name: Francis

  imports:
    - {target_file.name}
"""

            with NamedTemporaryFile(mode="w+", suffix=".yml") as source_file:
                source_file.write(source_yaml)
                source_file.flush()
                source_file.seek(0)

                # Run the operation from the imported config
                with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                    DyngleApp.start(
                        "--config", source_file.name, "run", "doit", debug=True
                    )

        # stdout is captured to variables, so trap should be empty
        self.assertEqual(t.captured, "")

    def test_nested_imports_with_values(self):
        """
        Test that constants propagate through multiple levels of imports.

        Scenario:
        - Config A defines constant 'outer'
        - Config A imports Config B
        - Config B defines constant 'middle' and imports Config C
        - C defines constant 'inner' and an operation that uses all 3 constants
        - All constants should be accessible in Config C's operation
        """
        # Create innermost config (C)
        inner_yaml = """
dyngle:
  constants:
    inner: InnerValue
  operations:
    test:
      - echo {{inner}} => i
      - echo {{middle}} => m
      - echo {{outer}} => o
"""

        with NamedTemporaryFile(
            mode="w+", suffix=".yml", delete=False
        ) as inner_file:
            inner_file.write(inner_yaml)
            inner_file.flush()
            inner_file.seek(0)

            # Create middle config (B)
            middle_yaml = f"""
dyngle:
  constants:
    middle: MiddleValue
  imports:
    - {inner_file.name}
"""

            with NamedTemporaryFile(
                mode="w+", suffix=".yml", delete=False
            ) as mf:
                mf.write(middle_yaml)
                mf.flush()
                mf.seek(0)

                # Create outer config (A)
                outer_yaml = f"""
dyngle:
  constants:
    outer: OuterValue
  imports:
    - {mf.name}
"""

                with NamedTemporaryFile(mode="w+", suffix=".yml") as of:
                    of.write(outer_yaml)
                    of.flush()
                    of.seek(0)

                    # Run the operation from the innermost imported config
                    with self.subprocess_runner_trap() as t, \
                            self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                        DyngleApp.start(
                            "--config", of.name, "run", "test", debug=True
                        )

        # stdout is captured to variables, so trap should be empty
        self.assertEqual(t.captured, "")
