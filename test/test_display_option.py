from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp

from test import DyngleTestCase


class TestDisplayOption(DyngleTestCase):

    def test_display_steps_shows_command_step(self):
        """When display=steps, CommandStep should print its markup"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"t": ["echo hello"]}}}
        )
        with self.patchout() as o, self.patcherr() as e, \
                self.mock_subprocess_runner(), self.patch_stream(""):
            a.parse_run("run", "t", "--display", "steps")
        self.assertIn("echo hello", e.getvalue())

    def test_display_none_suppresses_output(self):
        """When display=none, no step markup should be printed"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"t": ["echo hello"]}}}
        )
        with self.patchout() as o, self.patcherr() as e, \
                self.mock_subprocess_runner(), self.patch_stream(""):
            a.parse_run("run", "t", "--display", "none")
        # Should not contain the step markup
        self.assertNotIn("echo hello", e.getvalue())

    def test_display_defaults_to_steps(self):
        """When no --display option, default should be 'steps'"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"t": ["echo hello"]}}}
        )
        with self.patchout() as o, self.patcherr() as e, \
                self.mock_subprocess_runner(), self.patch_stream(""):
            a.parse_run("run", "t")
        self.assertIn("echo hello", e.getvalue())

    def test_display_with_multiple_steps(self):
        """Multiple CommandSteps should each display their markup"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {"t": ["echo first", "echo second"]}
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e, \
                self.mock_subprocess_runner(), self.patch_stream(""):
            a.parse_run("run", "t", "--display", "steps")
        err = e.getvalue()
        self.assertIn("echo first", err)
        self.assertIn("echo second", err)

    def test_display_with_suboperation(self):
        """SubOperationStep should not display anything for now"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "a": ["echo from a"],
                        "b": [{"sub": "a"}],
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e, \
                self.mock_subprocess_runner(), self.patch_stream(""):
            a.parse_run("run", "b", "--display", "steps")
        err = e.getvalue()
        # Should show the CommandStep from suboperation
        self.assertIn("echo from a", err)

    def test_display_with_templates(self):
        """Display should show step before template resolution"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"t": ["echo {{value}}"]}}}
        )
        with self.patchout() as o, self.patcherr() as e, \
                self.mock_subprocess_runner(), self.patch_stream(
            "value: xyz"
        ):
            a.parse_run("run", "t", "--display", "steps")
        # Should display original template, not resolved value
        self.assertIn("echo {{value}}", e.getvalue())
