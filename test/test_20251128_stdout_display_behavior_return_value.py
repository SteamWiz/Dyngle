from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from test import DyngleTestCase


class TestStdoutDisplayBehaviorReturnValue(DyngleTestCase):
    """Test stdout display behavior based on return value presence."""

    def test_operation_without_return_shows_stdout(self):
        """Operations without return: should show stdout (script-like)"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "script_op": ["echo hello world"]
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
            a.parse_run("run", "script_op")
        
        # Should have captured stdout since no return: key
        self.assertEqual(t.captured.strip(), "hello world")

    def test_operation_with_return_suppresses_stdout(self):
        """Operations with return: should suppress stdout (function-like)"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "func_op": {
                            "returns": "result",
                            "steps": [
                                "echo should not appear",
                                "echo visible => result"
                            ]
                        }
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
            a.parse_run("run", "func_op")
        
        # Should NOT have captured stdout from first echo
        # (second echo is captured with => so also doesn't appear)
        self.assertEqual(t.captured, "")

    def test_operation_with_return_and_capture_suppresses_both(self):
        """Operations with return: suppress uncaptured, capture goes to data"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "func_op": {
                            "returns": "result",
                            "steps": [
                                "echo hidden",
                                "echo captured => result"
                            ]
                        }
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
            result = a.parse_run("run", "func_op")
        
        # No stdout should appear
        self.assertEqual(t.captured, "")
        # Return value should be the captured output
        o.seek(0)
        self.assertEqual(o.read().strip(), "captured")

    def test_suboperation_inherits_script_behavior(self):
        """Sub-operations inherit script behavior from parent without return:"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "helper": ["echo helper output"],
                        "parent_script": [
                            "echo parent output",
                            {"sub": "helper"}
                        ]
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
            a.parse_run("run", "parent_script")
        
        stdout = t.captured
        # Both parent and helper output should be visible
        self.assertIn("parent output", stdout)
        self.assertIn("helper output", stdout)

    def test_suboperation_inherits_function_behavior(self):
        """Sub-operations inherit function behavior from parent with return:"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "helper": ["echo helper output"],
                        "parent_func": {
                            "returns": "result",
                            "steps": [
                                "echo parent output",
                                {"sub": "helper"},
                                "echo done => result"
                            ]
                        }
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
            a.parse_run("run", "parent_func")
        
        # No stdout should appear from either parent or helper
        self.assertEqual(t.captured, "")

    def test_captured_output_still_works_in_script_mode(self):
        """Script mode with => capture should still suppress that output"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "mixed_script": [
                            "echo visible",
                            "echo captured => data"
                        ]
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
            a.parse_run("run", "mixed_script")
        
        stdout = t.captured
        # Only the uncaptured echo should be visible
        self.assertIn("visible", stdout)
        self.assertNotIn("captured", stdout)
