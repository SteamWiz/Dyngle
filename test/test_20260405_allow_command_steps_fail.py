from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.context import Context
from test import DyngleTestCase


class TestAllowCommandStepsFail(DyngleTestCase):
    """Test that command steps with ignore-errors: true continue on nonzero exit"""

    def test_nonzero_exit_raises_by_default(self):
        """A command step that exits nonzero raises DyngleError by default"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"test": {"steps": ["grep nothing /dev/null"]}}}}
        )

        with self.patchout(), self.patcherr(), self.mock_subprocess_runner() as p:
            p.return_value = 1, ""
            with self.assertRaises(DyngleError):
                a.toolset.operations["test"].run(Context())

    def test_ignore_errors_continues_on_nonzero(self):
        """A command step with ignore-errors: true does not raise on nonzero exit"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {
                            "steps": [
                                {
                                    "command": "grep nothing /dev/null",
                                    "ignore-errors": True,
                                }
                            ]
                        }
                    }
                }
            }
        )

        with self.patchout(), self.patcherr(), self.mock_subprocess_runner() as p:
            p.return_value = 1, ""
            # Should not raise
            a.toolset.operations["test"].run(Context())

    def test_ignore_errors_captures_output_on_nonzero(self):
        """Output is still captured via => even when exit code is nonzero"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {
                            "returns": "line-count",
                            "steps": [
                                {
                                    "command": "grep -c nothing /dev/null => line-count",
                                    "ignore-errors": True,
                                }
                            ],
                        }
                    }
                }
            }
        )

        with self.patchout(), self.patcherr(), self.mock_subprocess_runner() as p:
            p.return_value = 1, "0"
            result = a.toolset.operations["test"].run(Context())

        self.assertEqual(result, "0")

    def test_ignore_errors_false_still_raises(self):
        """Explicitly setting ignore-errors: false raises on nonzero exit"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {
                            "steps": [{"command": "false", "ignore-errors": False}]
                        }
                    }
                }
            }
        )

        with self.patchout(), self.patcherr(), self.mock_subprocess_runner() as p:
            p.return_value = 1, ""
            with self.assertRaises(DyngleError):
                a.toolset.operations["test"].run(Context())

    def test_dict_command_step_executes_correct_command(self):
        """Dict-form command step passes the correct argv to the subprocess"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {
                            "steps": [{"command": "echo hello", "ignore-errors": True}]
                        }
                    }
                }
            }
        )

        with self.patchout(), self.patcherr(), self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())

        self.assertEqual(p.call_args.args[0], ["echo", "hello"])
