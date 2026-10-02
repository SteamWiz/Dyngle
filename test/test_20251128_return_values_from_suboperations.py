from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.context import Context
from test import DyngleTestCase


class TestReturnValuesFromSuboperations(DyngleTestCase):
    """Test send: and receive: attributes for sub-operation steps"""

    def test_output_captures_return_value_string(self):
        """Test that output: captures a string return value from sub-operation"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "msg",
                            "steps": ['echo "hello" => msg'],
                        },
                        "parent": {
                            "steps": [
                                {"sub": "child", "receive": "result"},
                                'echo "{{result}}"'
                            ],
                            "returns": "result"
                        },
                    }
                }
            }
        )
        
        with self.subprocess_runner_trap() as t, self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        # Result should be captured in parent's data
        self.assertEqual(r, "hello")

    def test_output_captures_return_value_dict(self):
        """Test that output: can capture a dict return value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "obj",
                            "constants": {"obj": {"x": 1, "y": 2}},
                            "steps": ['echo "done"'],
                        },
                        "parent": {
                            "steps": [
                                {"sub": "child", "receive": "result"}
                            ],
                            "returns": "result"
                        },
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        self.assertEqual(r, {"x": 1, "y": 2})

    def test_output_captures_return_value_list(self):
        """Test that output: can capture a list return value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "items",
                            "constants": {"items": [1, 2, 3]},
                            "steps": ['echo "done"'],
                        },
                        "parent": {
                            "steps": [
                                {"sub": "child", "receive": "result"}
                            ],
                            "returns": "result"
                        },
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        self.assertEqual(r, [1, 2, 3])

    def test_input_passes_dict_to_suboperation(self):
        """Test that input: passes dict keys/values as sub-operation context"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "name",
                            "steps": ['echo "Hello {{name}}" => greeting'],
                        },
                        "parent": {
                            "steps": [
                                {"sub": "child", "send": "data", "receive": "result"}
                            ],
                            "returns": "result"
                        },
                    },
                    "constants": {"data": {"name": "Alice", "age": 30}},
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        # Child should receive name from the input dict
        self.assertEqual(r, "Alice")

    def test_input_passes_nested_dict_to_suboperation(self):
        """Test that input: can pass a nested dict value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "config.port",
                            "steps": ['echo "{{config.host}}"'],
                        },
                        "parent": {
                            "steps": [
                                {"sub": "child", "send": "settings", "receive": "result"}
                            ],
                            "returns": "result"
                        },
                    },
                    "constants": {
                        "settings": {"config": {"host": "localhost", "port": 8080}}
                    },
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        self.assertEqual(r, 8080)

    def test_input_with_multiple_keys(self):
        """Test that input: passes multiple keys from dict"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "result",
                            "expressions": {"result": "x + y"},
                            "steps": ['echo "computing"'],
                        },
                        "parent": {
                            "steps": [
                                {"sub": "child", "send": "nums", "receive": "sum"}
                            ],
                            "returns": "sum"
                        },
                    },
                    "constants": {"nums": {"x": 3, "y": 7}},
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        self.assertEqual(r, 10)

    def test_input_isolates_suboperation_data(self):
        """Test that input: prevents sub-operation from accessing parent's full data"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "msg",
                            "steps": ['echo "{{msg}}" => msg'],
                        },
                        "parent": {
                            "steps": [
                                'echo "parent_secret" => secret',
                                'echo "shared_msg" => msg',
                                {"sub": "child", "send": "subset", "receive": "result"}
                            ],
                            "returns": "my-result",
                            "expressions": {
                                "my-result": {
                                    "result": "result",
                                    "secret": "secret"
                                }
                            }
                        }
                    },
                    "constants": {"subset": {"msg": "from_dict"}},
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        # Child should only see msg from subset dict, not from parent data
        self.assertEqual(r["result"], "from_dict")
        self.assertEqual(r["secret"], "parent_secret")

    def test_input_and_output_together(self):
        """Test using both input: and output: in same sub-operation call"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "double": {
                            "returns": "result",
                            "expressions": {"result": "num * 2"},
                            "steps": ['echo "doubling"'],
                        },
                        "main": {
                            "steps": [
                                {"sub": "double", "send": "params", "receive": "doubled"},
                                'echo "{{doubled}}"'
                            ],
                            "returns": "doubled"
                        },
                    },
                    "constants": {"params": {"num": 5}},
                }
            }
        )
        
        with self.subprocess_runner_trap() as t, self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["main"].run(data, [])
        
        self.assertEqual(r, 10)

    def test_output_without_return_stores_none(self):
        """Test that output: stores None when sub-operation has no return:"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": ['echo "no return"'],
                        "parent": {
                            "steps": [
                                {"sub": "child", "receive": "result"}
                            ],
                            "returns": "result"
                        },
                    }
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        self.assertIsNone(r)

    def test_input_with_dotted_path(self):
        """Test that input: works with dotted paths to resolve nested dicts"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": {
                            "returns": "port",
                            "steps": ['echo "{{port}}"'],
                        },
                        "parent": {
                            "steps": [
                                {"sub": "child", "send": "settings.server", "receive": "result"}
                            ],
                            "returns": "result"
                        },
                    },
                    "constants": {"settings": {"server": {"port": 3000, "host": "0.0.0.0"}}},
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            r = a.toolset.operations["parent"].run(data, [])
        
        self.assertEqual(r, 3000)

    def test_input_requires_dict_type(self):
        """Test that input: raises error if resolved value is not a dict"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "child": ['echo "test"'],
                        "parent": [{"sub": "child", "send": "notadict"}],
                    },
                    "constants": {"notadict": "string_value"},
                }
            }
        )
        
        with self.patchout(), self.patcherr():
            data = Context()
            with self.assertRaises(DyngleError) as cm:
                a.toolset.operations["parent"].run(data, [])
