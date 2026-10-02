from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.model.context import Context
from test import DyngleTestCase


class TestOperationReturnValue(DyngleTestCase):
    """Test the return: attribute for operations"""

    def test_return_from_data_output(self):
        """Test returning a value that was captured to data with =>"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_value": {
                            "returns": "result",
                            "steps": ['echo "hello world" => result'],
                        }
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            result = a.toolset.operations["get_value"].run(data, [])
        
        self.assertEqual(result, "hello world")

    def test_return_from_local_constant(self):
        """Test returning a value from operation's local constants"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_constant": {
                            "returns": "greeting",
                            "constants": {"greeting": "Hello World"},
                            "steps": ['echo "{{greeting}}"'],
                        }
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            result = a.toolset.operations["get_constant"].run(data, [])
        
        self.assertEqual(result, "Hello World")

    def test_return_from_expression(self):
        """Test returning a computed expression value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "compute": {
                            "returns": "computed",
                            "expressions": {"computed": "'Result: ' + value"},
                            "steps": ['echo "test" => value'],
                        }
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            result = a.toolset.operations["compute"].run(data, [])
        
        self.assertEqual(result, "Result: test")

    def test_return_none_when_not_specified(self):
        """Test that operations without return: attribute return None"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {"no_return": ['echo "hello" => output']}
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            result = a.toolset.operations["no_return"].run(data, [])
        
        self.assertIsNone(result)

    def test_return_from_shared_data(self):
        """Test returning a value from shared data set by parent operation"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "parent": [
                            'echo "parent_value" => shared',
                            {"sub": "child"},
                        ],
                        "child": {
                            "returns": "shared",
                            "steps": ['echo "child executed"'],
                        },
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            # Run child directly with pre-populated data
            data["shared"] = "parent_value"
            result = a.toolset.operations["child"].run(data, [])
        
        self.assertEqual(result, "parent_value")

    def test_return_data_priority_over_constant(self):
        """Test that data values take priority over constants when both exist"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "priority_test": {
                            "returns": "value",
                            "constants": {"value": "constant"},
                            "steps": ['echo "data" => value'],
                        }
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            result = a.toolset.operations["priority_test"].run(data, [])
        
        # Data should take priority
        self.assertEqual(result, "data")
