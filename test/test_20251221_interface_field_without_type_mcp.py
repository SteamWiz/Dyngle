import asyncio
import json
from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.command.mcp_command import McpCommand
from test import DyngleTestCase, mcp_call_tool, mcp_list_tools


class TestInterfaceFieldWithoutTypeMcp(DyngleTestCase):

    def test_field_without_type_in_mcp_server(self):
        """Interface field without type should work in MCP server"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "print": {
                            "accepts": {
                                "message": None,  # No type specified
                            },
                            "steps": ['echo {{message}}'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            result = await mcp_list_tools(server)
            tool = next(t for t in result.tools if t.name == "print")
            
            # Tool should have input schema with message field
            props = tool.input_schema.get("properties", {})
            self.assertIn("message", props)
            # Field without explicit type should default to string
            self.assertEqual(props["message"]["type"], "string")
            
            # Field should NOT be required (has blank default)
            required = tool.input_schema.get("required", [])
            self.assertNotIn("message", required)

        with self.patcherr():
            asyncio.run(run_test())

    def test_field_with_empty_dict_in_mcp_server(self):
        """Interface field with empty dict definition should work"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "greet": {
                            "accepts": {
                                "name": {},  # Empty dict - no explicit type
                            },
                            "steps": ['echo "Hello {{name}}"'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            result = await mcp_list_tools(server)
            tool = next(t for t in result.tools if t.name == "greet")
            
            # Tool should have input schema with name field
            props = tool.input_schema.get("properties", {})
            self.assertIn("name", props)
            # Field without explicit type should default to string
            self.assertEqual(props["name"]["type"], "string")

        with self.patcherr():
            asyncio.run(run_test())

    def test_call_tool_with_field_without_type(self):
        """Calling tool with interface field without type should work"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "print": {
                            "accepts": {
                                "message": None,
                            },
                            "returns": "output",
                            "steps": ['echo "{{message}}" => output'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            result = await mcp_call_tool(server, "print", {"message": "Hello"})
            
            # Should return success with result
            content = result.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "Hello")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_field_with_additional_properties(self):
        """Field with additional JSON Schema properties should work"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "process": {
                            "accepts": {
                                "count": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 100,
                                }
                            },
                            "steps": ['echo "{{count}}"'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            result = await mcp_list_tools(server)
            tool = next(t for t in result.tools if t.name == "process")
            
            # Tool should have input schema with additional properties
            props = tool.input_schema.get("properties", {})
            self.assertIn("count", props)
            self.assertEqual(props["count"]["type"], "integer")
            self.assertEqual(props["count"]["minimum"], 1)
            self.assertEqual(props["count"]["maximum"], 100)

        with self.patcherr():
            asyncio.run(run_test())

    def test_field_without_type_gets_blank_default(self):
        """Field without type should get blank string default"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "greet": {
                            "accepts": {
                                "name": None,
                            },
                            "returns": "msg",
                            "steps": ['echo "Hello_{{name}}" => msg'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            # Call without providing the name field
            result = await mcp_call_tool(server, "greet", {})
            
            # Should return success with blank name (underscore shows blank)
            content = result.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "Hello_")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_mixed_fields_with_and_without_types(self):
        """Mix of fields with and without explicit types should work"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "process": {
                            "accepts": {
                                "name": None,  # No type - defaults to string
                                "age": {"type": "integer"},  # Explicit type
                                "active": {},  # Empty dict - defaults to string
                            },
                            "returns": "result",
                            "steps": [
                                'echo "{{name}},{{age}},{{active}}" => result'
                            ],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            # Check schema
            list_result = await mcp_list_tools(server)
            tool = next(t for t in list_result.tools 
                       if t.name == "process")
            
            props = tool.input_schema.get("properties", {})
            self.assertEqual(props["name"]["type"], "string")
            self.assertEqual(props["age"]["type"], "integer")
            self.assertEqual(props["active"]["type"], "string")
            
            # Call with values
            call_result = await mcp_call_tool(
                server,
                "process",
                {"name": "Alice", "age": 25, "active": "yes"},
            )
            
            content = call_result.content[0]
            data = json.loads(content.text)
            self.assertEqual(data["result"], "Alice,25,yes")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())
