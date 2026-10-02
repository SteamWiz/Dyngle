from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp

from test import DyngleTestCase


class TestRunCommandReturn(DyngleTestCase):
    """Test that run command prints return values"""

    def test_return_string_value(self):
        """String return values should be printed as-is"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_msg": {
                            "returns": "msg",
                            "steps": ['echo "hello" => msg'],
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e:
            a.parse_run("run", "get_msg")
        self.assertIn("hello", o.getvalue())

    def test_return_string_constant(self):
        """String constants should be printed without YAML formatting"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_text": {
                            "returns": "message",
                            "constants": {"message": "plain text"},
                            "steps": ['echo "done"'],
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e:
            a.parse_run("run", "get_text")
        self.assertEqual("plain text", o.getvalue().strip())

    def test_return_dict_as_yaml(self):
        """Dict return values should be printed as YAML"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_dict": {
                            "returns": "data",
                            "constants": {
                                "data": {"name": "test", "value": 42}
                            },
                            "steps": ['echo "done"'],
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e:
            a.parse_run("run", "get_dict")
        output = o.getvalue()
        self.assertIn("name: test", output)
        self.assertIn("value: 42", output)

    def test_return_list_as_yaml(self):
        """List return values should be printed as YAML"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_list": {
                            "returns": "items",
                            "constants": {"items": ["one", "two", "three"]},
                            "steps": ['echo "done"'],
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e:
            a.parse_run("run", "get_list")
        output = o.getvalue()
        self.assertIn("- one", output)
        self.assertIn("- two", output)
        self.assertIn("- three", output)

    def test_return_int_value(self):
        """Integer return values should be printed as-is"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_num": {
                            "returns": "num",
                            "constants": {"num": 42},
                            "steps": ['echo "done"'],
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e:
            a.parse_run("run", "get_num")
        self.assertIn("42", o.getvalue())

    def test_no_return_prints_nothing(self):
        """Operations without return should not print extra output"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {"no_ret": ['echo "test" => output']}
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e:
            a.parse_run("run", "no_ret")
        output = o.getvalue()
        # Should only have status message, not "None" or similar
        self.assertNotIn("None", output)
        # Just verify it doesn't crash

    def test_return_nested_structure(self):
        """Nested dicts/lists should be formatted as YAML"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_nested": {
                            "returns": "data",
                            "constants": {
                                "data": {
                                    "users": [
                                        {"name": "Alice", "age": 30},
                                        {"name": "Bob", "age": 25},
                                    ]
                                }
                            },
                            "steps": ['echo "done"'],
                        }
                    }
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e:
            a.parse_run("run", "get_nested")
        output = o.getvalue()
        self.assertIn("users:", output)
        self.assertIn("name: Alice", output)
        self.assertIn("age: 30", output)
