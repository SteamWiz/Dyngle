from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp

from test import DyngleTestCase


class TestOperationDescriptions(DyngleTestCase):

    def test_operation_with_description(self):
        """Operation should store description from config"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {
                            "description": "Test operation",
                            "steps": ["echo hello"]
                        }
                    }
                }
            }
        )
        op = a.toolset.operations["test"]
        self.assertEqual(op.description, "Test operation")

    def test_operation_without_description(self):
        """Operation without description should have None"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": ["echo hello"]
                    }
                }
            }
        )
        op = a.toolset.operations["test"]
        self.assertIsNone(op.description)

    def test_operation_with_empty_description(self):
        """Operation with explicit empty description"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {
                            "description": "",
                            "steps": ["echo hello"]
                        }
                    }
                }
            }
        )
        op = a.toolset.operations["test"]
        self.assertEqual(op.description, "")


class TestListOperationsCommand(DyngleTestCase):

    def test_list_single_operation_with_description(self):
        """List single operation with description"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {
                            "description": "Test description",
                            "steps": ["echo hello"]
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr():
            a.parse_run("list-operations")
        output = o.getvalue()
        self.assertIn("operations:", output)
        self.assertIn("test: Test description", output)

    def test_list_operation_without_description(self):
        """List operation without description shows empty"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": ["echo hello"]
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr():
            a.parse_run("list-operations")
        output = o.getvalue()
        self.assertIn("operations:", output)
        self.assertIn("test:", output)

    def test_list_multiple_operations(self):
        """List multiple operations with mixed descriptions"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "first": {
                            "description": "First op",
                            "steps": ["echo 1"]
                        },
                        "second": ["echo 2"],
                        "third": {
                            "description": "Third op",
                            "steps": ["echo 3"]
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr():
            a.parse_run("list-operations")
        output = o.getvalue()
        self.assertIn("operations:", output)
        self.assertIn("first: First op", output)
        self.assertIn("second:", output)
        self.assertIn("third: Third op", output)

    def test_list_operations_yaml_format(self):
        """Output should be valid YAML"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "op1": {
                            "description": "Description one",
                            "steps": ["echo 1"]
                        },
                        "op2": {
                            "description": "Description two",
                            "steps": ["echo 2"]
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr():
            a.parse_run("list-operations")
        output = o.getvalue()
        # Should be parseable as YAML
        from yaml import safe_load
        data = safe_load(output)
        self.assertIsInstance(data, dict)
        self.assertIn("operations", data)
        self.assertEqual(data["operations"]["op1"], "Description one")
        self.assertEqual(data["operations"]["op2"], "Description two")

    def test_list_operations_empty(self):
        """Handle empty operations gracefully"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {}
                }
            }
        )
        with self.patchout() as o, self.patcherr():
            a.parse_run("list-operations")
        output = o.getvalue()
        self.assertIn("operations:", output)
