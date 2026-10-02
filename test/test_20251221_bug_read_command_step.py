from tempfile import NamedTemporaryFile
from unittest.mock import Mock, patch

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestBugReadCommandStep(DyngleTestCase):

    def test_prompt_step_without_receive(self):
        """Test prompt step that just waits for user input"""
        y = {
            "dyngle": {
                "operations": {
                    "wait": [
                        {"prompt": "Press enter to continue"},
                        "echo done"
                    ]
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            m = Mock()
            m.return_value = ""
            with self.subprocess_runner_trap() as t:
                with self.patch_stream(""):
                    with self.patchout() as o:
                        with self.patcherr() as e:
                            with patch(
                                "wizlib.ui.shell_ui.ShellUI.get_text", m
                            ):
                                DyngleApp.start(
                                    "--config", f.name, "run", "wait", 
                                    debug=True
                                )
        # Verify prompt was called with correct message
        m.assert_called_once_with("Press enter to continue")
        # Verify echo was executed
        self.assertIn("done", t.captured)

    def test_prompt_step_with_receive(self):
        """Test prompt step that captures input into a variable"""
        y = {
            "dyngle": {
                "operations": {
                    "get-name": [
                        {"prompt": "Enter your name: ", "receive": "user-name"},
                        "echo Hello {{user-name}}"
                    ]
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            m = Mock()
            m.return_value = "Alice"
            with self.subprocess_runner_trap() as t:
                with self.patch_stream(""):
                    with self.patchout() as o:
                        with self.patcherr() as e:
                            with patch(
                                "wizlib.ui.shell_ui.ShellUI.get_text", m
                            ):
                                DyngleApp.start(
                                    "--config", f.name, "run", "get-name", 
                                    debug=True
                                )
        # Verify prompt was called
        m.assert_called_once_with("Enter your name: ")
        # Verify the captured input was used in the template
        self.assertIn("Hello Alice", t.captured)

    def test_prompt_step_with_template_in_message(self):
        """Test that prompt message supports template substitution"""
        y = {
            "dyngle": {
                "constants": {"app-name": "MyApp"},
                "operations": {
                    "greet": [
                        {"prompt": "Welcome to {{app-name}}! Press enter"},
                    ]
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            m = Mock()
            m.return_value = ""
            with self.patch_stream(""):
                with self.patchout() as o:
                    with self.patcherr() as e:
                        with patch(
                            "wizlib.ui.shell_ui.ShellUI.get_text", m
                        ):
                            DyngleApp.start(
                                "--config", f.name, "run", "greet", 
                                debug=True
                            )
        # Verify template was resolved in prompt
        m.assert_called_once_with("Welcome to MyApp! Press enter")
