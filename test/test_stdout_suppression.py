from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp

from test import DyngleTestCase


class TestStdoutSuppression(DyngleTestCase):
    """Test that stdout is suppressed when CommandStep has no output"""

    def test_stdout_dies_without_output_setting(self):
        """When operation has return:, stdout should be suppressed"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "echo_test": {
                            "constants": {"result": "x"},
                            "returns": "result",
                            "steps": ["echo hello world"]
                        }
                    }
                }
            }
        )
        
        # Use subprocess_runner_trap to capture what's sent to stdout
        with (
            self.subprocess_runner_trap() as t,
            self.patchout() as o,
            self.patcherr() as e,
            self.patch_stream("")
        ):
            a.parse_run("run", "echo_test")
        
        # The trap should NOT have captured any stdout when return: is set
        # (the output should have been suppressed/sent to DEVNULL)
        self.assertEqual(t.captured, "")

    def test_stdout_captured_with_output_setting(self):
        """When a CommandStep has => output, stdout should be captured"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "capture_test": ['echo "test output" => result']
                    }
                }
            }
        )
        
        with (
            self.subprocess_runner_trap() as t,
            self.patchout() as o,
            self.patcherr() as e,
            self.patch_stream("")
        ):
            a.parse_run("run", "capture_test")
        
        # When using =>, stdout should NOT appear in trap
        # (it's captured by the application)
        self.assertEqual(t.captured, "")

    def test_stderr_output_displayed(self):
        """When a command writes to stderr, it should be displayed"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "stderr_test": ['python3 -c "import sys; sys.stderr.write(\'error message\\n\')"']
                    }
                }
            }
        )
        
        with (
            self.patchout() as o,
            self.patcherr() as e,
            self.patch_stream("")
        ):
            a.parse_run("run", "stderr_test", "--display", "none")
        
        # Stderr from the subprocess should appear in our stderr
        self.assertIn("error message", e.getvalue())
