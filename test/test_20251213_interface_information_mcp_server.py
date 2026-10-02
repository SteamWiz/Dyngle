import asyncio
import json
from wizlib.config_handler import ConfigHandler
from mcp.types import ListToolsRequest, CallToolRequest

from dyngle import DyngleApp
from dyngle.command.mcp_command import McpCommand
from test import DyngleTestCase


class TestInterfaceInformationMcpServer(DyngleTestCase):

    def test_tool_with_interface_uses_interface_fields(self):
        """Operation with interface should use interface fields as inputs"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "greet": {
                            "accepts": {
                                "name": {"type": "string"},
                                "age": {"type": "integer"},
                            },
                            "steps": ['echo "Hello {{name}}, age {{age}}"'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            handler = server.request_handlers[ListToolsRequest]
            result = await handler(ListToolsRequest())
            tool = next(t for t in result.root.tools if t.name == "greet")
            
            # Tool should have input schema with interface fields
            props = tool.inputSchema.get("properties", {})
            self.assertIn("name", props)
            self.assertIn("age", props)
            self.assertEqual(props["name"]["type"], "string")
            self.assertEqual(props["age"]["type"], "integer")
            
            # String fields get blank defaults so are optional
            # Non-string fields without defaults are required
            required = tool.inputSchema.get("required", [])
            self.assertNotIn("name", required)  # String - has blank default
            self.assertIn("age", required)  # Integer - no default

        with self.patcherr():
            asyncio.run(run_test())

    def test_tool_without_interface_has_no_params(self):
        """Operation without interface should have no parameters"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "process": {
                            "steps": ['echo "test"'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            handler = server.request_handlers[ListToolsRequest]
            result = await handler(ListToolsRequest())
            tool = next(t for t in result.root.tools if t.name == "process")
            
            # Tool should have no parameters
            props = tool.inputSchema.get("properties", {})
            self.assertEqual(len(props), 0)
            
            # No required parameters
            required = tool.inputSchema.get("required", [])
            self.assertEqual(len(required), 0)

        with self.patcherr():
            asyncio.run(run_test())

    def test_call_tool_with_interface_passes_as_data(self):
        """Calling tool with interface should pass params as data dict"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "greet": {
                            "accepts": {
                                "name": {"type": "string"},
                            },
                            "returns": "msg",
                            "steps": ['echo "Hello {{name}}" => msg'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            handler = server.request_handlers[CallToolRequest]
            result = await handler(
                CallToolRequest(
                    params={"name": "greet", "arguments": {"name": "Alice"}}
                )
            )
            
            # Should return success with result
            content = result.root.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "Hello Alice")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_call_tool_without_interface_has_no_data(self):
        """Calling tool without interface should have empty data context"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "process": {
                            "returns": "result",
                            "steps": ['echo "Done" => result'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            handler = server.request_handlers[CallToolRequest]
            result = await handler(
                CallToolRequest(
                    params={
                        "name": "process",
                        "arguments": {},
                    }
                )
            )
            
            # Should return success with result
            content = result.root.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "Done")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_interface_with_nested_objects(self):
        """Interface with nested objects should work correctly"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "info": {
                            "accepts": {
                                "user": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "age": {"type": "integer"},
                                    },
                                }
                            },
                            "returns": "msg",
                            "steps": [
                                'echo "{{user.name}} is {{user.age}}" => msg'
                            ],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            handler = server.request_handlers[CallToolRequest]
            result = await handler(
                CallToolRequest(
                    params={
                        "name": "info",
                        "arguments": {
                            "user": {"name": "Bob", "age": 30}
                        },
                    }
                )
            )
            
            # Should return success
            content = result.root.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "Bob is 30")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_no_longer_uses_args_expressions(self):
        """Operations with args expressions but no interface have no params"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "search": {
                            "expressions": {
                                "query": "args[0]",
                                "limit": "args[1] if len(args) > 1 else '10'",
                            },
                            "steps": [
                                'echo "Query: {{query}}, Limit: {{limit}}"'
                            ],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            handler = server.request_handlers[ListToolsRequest]
            result = await handler(ListToolsRequest())
            tool = next(t for t in result.root.tools if t.name == "search")
            
            # Tool should have no parameters
            props = tool.inputSchema.get("properties", {})
            self.assertEqual(len(props), 0)
            self.assertNotIn("query", props)
            self.assertNotIn("limit", props)
            self.assertNotIn("args", props)

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_interface_with_array_type(self):
        """Interface with array type should work correctly"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "process": {
                            "accepts": {
                                "items": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                }
                            },
                            "returns": "count",
                            "steps": ['echo "3" => count'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            # Check tool definition
            list_handler = server.request_handlers[ListToolsRequest]
            list_result = await list_handler(ListToolsRequest())
            tool = next(t for t in list_result.root.tools 
                       if t.name == "process")
            
            props = tool.inputSchema.get("properties", {})
            self.assertIn("items", props)
            self.assertEqual(props["items"]["type"], "array")
            
            # Test calling with array
            call_handler = server.request_handlers[CallToolRequest]
            call_result = await call_handler(
                CallToolRequest(
                    params={
                        "name": "process",
                        "arguments": {"items": ["a", "b", "c"]},
                    }
                )
            )
            
            content = call_result.root.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())
