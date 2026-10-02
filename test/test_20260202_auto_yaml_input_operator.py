from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.model.context import Context
from test import DyngleTestCase


class TestAutoYamlInputOperator(DyngleTestCase):

    def test_dict_converted_to_yaml(self):
        """Dict payload should be converted to YAML before stdin"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "o": {
                        "constants": {"d": {"a": 1, "b": 2}},
                        "returns": "r",
                        "steps": ["d -> cat => r"]
                    }
                }
            }
        })
        with self.patchout(), self.patcherr():
            r = a.toolset.operations["o"].run(Context(), [])
        # Should have YAML representation
        self.assertIn("a: 1", r)
        self.assertIn("b: 2", r)

    def test_list_converted_to_yaml(self):
        """List payload should be converted to YAML before stdin"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "o": {
                        "constants": {"l": ["x", "y", "z"]},
                        "returns": "r",
                        "steps": ["l -> cat => r"]
                    }
                }
            }
        })
        with self.patchout(), self.patcherr():
            r = a.toolset.operations["o"].run(Context(), [])
        # Should have YAML list representation
        self.assertIn("- x", r)
        self.assertIn("- y", r)
        self.assertIn("- z", r)

    def test_string_unchanged(self):
        """String payload should remain unchanged"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "o": {
                        "constants": {"s": "hello world"},
                        "returns": "r",
                        "steps": ["s -> cat => r"]
                    }
                }
            }
        })
        with self.patchout(), self.patcherr():
            r = a.toolset.operations["o"].run(Context(), [])
        # String should be passed as-is
        self.assertEqual(r, "hello world")

    def test_nested_structure_converted(self):
        """Nested structures should be properly serialized to YAML"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "o": {
                        "constants": {
                            "n": {"users": [{"name": "Alice", "age": 30}]}
                        },
                        "returns": "r",
                        "steps": ["n -> cat => r"]
                    }
                }
            }
        })
        with self.patchout(), self.patcherr():
            r = a.toolset.operations["o"].run(Context(), [])
        # Should have YAML representation of nested structure
        self.assertIn("users:", r)
        self.assertIn("name: Alice", r)
        self.assertIn("age: 30", r)

    def test_integer_converted_to_string(self):
        """Integer payload should be converted to string"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "o": {
                        "constants": {"i": 42},
                        "returns": "r",
                        "steps": ["i -> cat => r"]
                    }
                }
            }
        })
        with self.patchout(), self.patcherr():
            r = a.toolset.operations["o"].run(Context(), [])
        # Integer should be converted to string
        self.assertEqual(r, "42")
