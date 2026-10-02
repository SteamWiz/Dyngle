from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.context import Context
from test import DyngleTestCase


class TestExplicitOnlySubOperationsClearerNaming(DyngleTestCase):
    """Test new 'accept:', 'send:', 'receive:' terminology and
    explicit-only data flow for sub-operations"""

    def test_accept_defines_operation_input(self):
        """Test that accept: defines input schema"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "greet": {
                        "accepts": {"name": {"type": "string"}},
                        "steps": ['echo "Hello {{name}}"'],
                    }
                }
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context({"name": "Alice"})
            a.toolset.operations["greet"].run(d, [])
        
        self.assertEqual(d["name"], "Alice")

    def test_send_passes_data_to_suboperation(self):
        """Test that send: passes data to sub-operation"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "child": {
                        "returns": "name",
                        "steps": ['echo "{{name}}"'],
                    },
                    "parent": {
                        "steps": [
                            {"sub": "child", "send": "data", "receive": "result"}
                        ],
                        "returns": "result"
                    },
                },
                "constants": {"data": {"name": "Bob"}},
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertEqual(r, "Bob")

    def test_receive_captures_return_value(self):
        """Test that receive: captures return value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "child": {
                        "returns": "msg",
                        "steps": ['echo "hello" => msg'],
                    },
                    "parent": {
                        "steps": [
                            {"sub": "child", "receive": "result"}
                        ],
                        "returns": "result"
                    }
                }
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            # a.toolset.operations["parent"].run(d, [])
            r = a.toolset.operations["parent"].run(d, [])
        
        # self.assertEqual(d["result"], "hello")
        self.assertEqual(r, "hello")

    def test_implicit_data_sharing_removed(self):
        """Test that sub-operations no longer see parent's => data"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "child": {
                        "steps": ['echo "{{parent_data}}"'],
                    },
                    "parent": [
                        'echo "secret" => parent_data',
                        {"sub": "child"},
                    ],
                }
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            with self.assertRaises(DyngleError) as cm:
                a.toolset.operations["parent"].run(d, [])
            
            self.assertIn("parent_data", str(cm.exception))

    def test_explicit_send_isolates_data(self):
        """Test that send: creates isolated context"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "child": {
                        "returns": "shared",
                        "steps": ['echo "{{shared}}"'],
                    },
                    "parent": {
                        "steps": [
                            'echo "parent_val" => shared',
                            {"sub": "child", "send": "pkg", "receive": "result"}
                        ],
                        "returns": "result"
                    },
                },
                "constants": {"pkg": {"shared": "child_val"}},
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertEqual(r, "child_val")

    def test_send_and_receive_together(self):
        """Test using both send: and receive:"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "double": {
                        "returns": "result",
                        "expressions": {"result": "num * 2"},
                        "steps": ['echo "doubling"'],
                    },
                    "main": {
                        "steps": [
                            {"sub": "double", "send": "params", "receive": "doubled"}
                        ],
                        "returns": "doubled"
                    },
                },
                "constants": {"params": {"num": 5}},
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["main"].run(d, [])
        
        self.assertEqual(r, 10)

    def test_accept_validates_send_data(self):
        """Test that accept: validates data passed via send:"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "validate": {
                        "accepts": {"user_id": {"type": "string"}},
                        "steps": ['echo "{{user_id}}"'],
                    },
                    "caller": [
                        {"sub": "validate", "send": "user_data"},
                    ],
                },
                "constants": {"user_data": {"user_id": "123"}},
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            a.toolset.operations["caller"].run(d, [])

    def test_suboperation_without_send_gets_empty_context(self):
        """Test that sub-operations without send: get empty context"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "child": {
                        "returns": "msg",
                        "constants": {"msg": "from_child"},
                        "steps": ['echo "{{msg}}"'],
                    },
                    "parent": {
                        "steps": [
                            'echo "parent_data" => data',
                            {"sub": "child", "receive": "result"}
                        ],
                        "returns": "result"
                    }
                }
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertEqual(r, "from_child")

    def test_send_requires_dict_type(self):
        """Test that send: raises error if resolved value is not a dict"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "child": ['echo "test"'],
                    "parent": [{"sub": "child", "send": "notadict"}],
                },
                "constants": {"notadict": "string_value"},
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            with self.assertRaises(DyngleError) as cm:
                a.toolset.operations["parent"].run(d, [])
            
            self.assertIn("dict", str(cm.exception).lower())

    def test_receive_without_return_stores_none(self):
        """Test that receive: stores None when sub has no return:"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
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
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertIsNone(r)

    def test_send_with_dotted_path(self):
        """Test that send: works with dotted paths"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "child": {
                        "returns": "port",
                        "steps": ['echo "{{port}}"'],
                    },
                    "parent": {
                        "steps": [
                            {"sub": "child", "send": "settings.server", 
                             "receive": "result"}
                        ],
                        "returns": "result"
                    },
                },
                "constants": {
                    "settings": {"server": {"port": 3000, "host": "0.0.0.0"}}
                },
            }
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertEqual(r, 3000)

    def test_mcp_server_uses_accept_schema(self):
        """Test that MCP server uses accept: for tool input schema"""
        from dyngle.command.mcp_command import McpCommand
        from mcp.types import ListToolsRequest
        import asyncio
        
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test_op": {
                        "accepts": {"param": {"type": "string"}},
                        "steps": ['echo "{{param}}"'],
                    }
                }
            }
        })
        
        cmd = McpCommand(a)
        server = cmd.create_server()
        
        async def run_test():
            handler = server.request_handlers[ListToolsRequest]
            result = await handler(ListToolsRequest())
            t = next((x for x in result.root.tools if x.name == "test_op"), None)
            self.assertIsNotNone(t)
            self.assertIn("param", t.inputSchema["properties"])
        
        with self.patcherr():
            asyncio.run(run_test())

    def test_receive_captures_dict_return(self):
        """Test that receive: can capture dict return value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
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
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertEqual(r, {"x": 1, "y": 2})

    def test_receive_captures_list_return(self):
        """Test that receive: can capture list return value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
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
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertEqual(r, [1, 2, 3])

    def test_send_passes_multiple_keys(self):
        """Test that send: passes multiple keys from dict"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
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
        })
        
        with self.patchout(), self.patcherr():
            d = Context()
            r = a.toolset.operations["parent"].run(d, [])
        
        self.assertEqual(r, 10)
