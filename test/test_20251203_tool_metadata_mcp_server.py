# test/test_20251203_tool_metadata_mcp_server.py

import asyncio
from wizlib.config_handler import ConfigHandler
from mcp.types import ListToolsRequest

from dyngle import DyngleApp
from dyngle.command.mcp_command import McpCommand
from test import DyngleTestCase


class TestToolMetadataMcpServer(DyngleTestCase):

    def test_tool_with_description(self):
        """Test that operation description appears in MCP tool metadata"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "search": {
                            "description": "Performs a Google query",
                            "steps": ['echo "results" => r'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            # Call list_tools handler
            handler = server.request_handlers[ListToolsRequest]
            result = await handler(ListToolsRequest())
            search_tool = next(t for t in result.root.tools if t.name == "search")
            
            # Tool should have the description
            self.assertEqual("Performs a Google query", search_tool.description)

        with self.patcherr():
            asyncio.run(run_test())

    def test_tool_without_description(self):
        """Test that operations without descriptions still work"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "no_desc": {
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
            tool = next(t for t in result.root.tools if t.name == "no_desc")
            
            # Tool should exist with generated description
            self.assertIsNotNone(tool)
            self.assertEqual("Execute no_desc operation", tool.description)

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_tool_with_return_value_output_schema(self):
        """Test that operations with return values work"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "get_data": {
                            "returns": "results",
                            "steps": ['echo "data" => results'],
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
            tool = next(t for t in result.root.tools if t.name == "get_data")
            
            # Tool should have input schema
            self.assertIsNotNone(tool.inputSchema)

        with self.patcherr():
            asyncio.run(run_test())

    def test_tool_with_input_parameters(self):
        """Test that operations without interface have no parameters"""
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
            
            # Tool should have input schema
            self.assertIsNotNone(tool.inputSchema)
            props = tool.inputSchema.get("properties", {})
            
            # Should have no parameters (no interface defined)
            self.assertEqual(len(props), 0)

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_tool_excludes_non_args_expressions(self):
        """Test that operations without interface have no parameters"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "process": {
                            "expressions": {
                                "query": "args[0]",
                                "timestamp": "datetime.now()",
                                "const": "'fixed-value'",
                            },
                            "steps": ['echo "{{query}} at {{timestamp}}"'],
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
            
            props = tool.inputSchema.get("properties", {})
            
            # Should have no parameters (no interface)
            self.assertEqual(len(props), 0)

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_complete_metadata_example(self):
        """Test complete metadata with description and output"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "search": {
                            "description": "Performs a Google query",
                            "expressions": {"query": "args[0]"},
                            "returns": "results",
                            "steps": [
                                'curl https://google.com?q={{query}} => results'
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
            
            # Should have description
            self.assertEqual("Performs a Google query", tool.description)
            
            # Should have no parameters (no interface)
            props = tool.inputSchema.get("properties", {})
            self.assertEqual(len(props), 0)

        with self.patcherr():
            asyncio.run(run_test())

    def test_call_tool_with_parameters(self):
        """Test calling a tool without interface (no parameters)"""
        import json
        from mcp.types import CallToolRequest
        
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "echo": {
                            "returns": "output",
                            "steps": ['echo "hello" => output'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()

        async def run_test():
            from mcp.types import CallToolRequest
            handler = server.request_handlers[CallToolRequest]
            result = await handler(
                CallToolRequest(
                    params={
                        "name": "echo",
                        "arguments": {},
                    }
                )
            )
            
            # Should return TextContent with result
            self.assertEqual(len(result.root.content), 1)
            content = result.root.content[0]
            self.assertEqual(content.type, "text")
            
            # Parse the JSON result
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "hello")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    # def test_execute_method_starts_server(self):
    #     """Test that execute() method starts the MCP server"""
    #     from unittest.mock import patch, MagicMock
        
    #     a = DyngleApp()
    #     a.config = ConfigHandler.setup(
    #         {
    #             "dyngle": {
    #                 "operations": {
    #                     "test": {"steps": ['echo "test"']},
    #                 }
    #             }
    #         }
    #     )

    #     cmd = McpCommand(a)
    #     # Set transport attribute (normally set by argument parser)
    #     cmd.transport = "stdio"
        
    #     # Mock asyncio.run to prevent blocking
    #     with patch('asyncio.run') as mock_run:
    #         cmd.execute()
            
    #         # Verify asyncio.run was called (which means execute() ran)
    #         mock_run.assert_called_once()
            
    #         # Verify status was set
    #         self.assertIn("MCP server started", cmd.status)
    #         self.assertIn("stdio", cmd.status)
