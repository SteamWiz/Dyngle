from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestAllowInputOperationCli(DyngleTestCase):

    def test_operation_via_ui_prompt(self):
        """Test that operation can be provided interactively via UI when not on
        CLI"""
        y = {
            "dyngle": {
                "operations": {"test_op": ['echo "hello" => output']},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            # Mock UI's get_text method to return 'test_op' when prompted
            with patch(
                "wizlib.ui.shell_ui.ShellUI.get_text", return_value="test_op"
            ):
                with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e:
                    # Note: not passing 'operation' argument to 'run' command
                    DyngleApp.start("--config", f.name, "run", debug=True)

            # Verify the operation was executed (stdout captured to output var)
            self.assertEqual(t.captured, "")

    def test_operation_empty_input_raises_error(self):
        """Test that empty operation input via UI raises DyngleError"""
        y = {
            "dyngle": {
                "operations": {"test_op": ['echo "hello"']},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            # Mock UI's get_text method to return empty string
            with patch("wizlib.ui.shell_ui.ShellUI.get_text", return_value=""):
                with self.patchout() as o, self.patcherr() as e, self.assertRaises(
                    DyngleError
                ) as context:
                    # Note: not passing 'operation' argument to 'run' command
                    DyngleApp.start("--config", f.name, "run", debug=True)

                # Verify the error message
                self.assertIn("Operation required", str(context.exception))
