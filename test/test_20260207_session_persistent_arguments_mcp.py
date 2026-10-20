import asyncio
import json
from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.command.mcp_command import McpCommand
from test import DyngleTestCase, mcp_call_tool


class TestSessionPersistentArgumentsMcp(DyngleTestCase):

    def test_mcp_command_accepts_args_parameter(self):
        """MCP command should accept args parameter like run command"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "echo": {
                            "returns": "result",
                            "steps": ['echo "{{args[0]}}" => result'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        cmd.args = ["test-value"]
        
        # Should not raise an error
        server = cmd.create_server()
        self.assertIsNotNone(server)

    def test_args_passed_to_operation_run(self):
        """Args from command line should be passed to operation.run()"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "expressions": {
                        "arg0": "args[0]",
                        "arg1": "args[1]"
                    },
                    "operations": {
                        "use-args": {
                            "returns": "result",
                            "steps": ['echo "arg0={{arg0}} arg1={{arg1}}" => result'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        cmd.args = ["first", "second"]
        server = cmd.create_server()

        async def run_test():
            result = await mcp_call_tool(server, "use-args", {})
            
            content = result.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "arg0=first arg1=second")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_args_empty_list_when_not_provided(self):
        """When no args provided, operations should receive empty list"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "expressions": {"arg_count": "len(args)"},
                    "operations": {
                        "count-args": {
                            "returns": "count",
                            "steps": ['echo "{{arg_count}}" => count'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        cmd.args = []
        server = cmd.create_server()

        async def run_test():
            result = await mcp_call_tool(server, "count-args", {})
            
            content = result.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "0")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_args_available_to_all_tool_calls(self):
        """Args should be available to all tool calls in the session"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "expressions": {"first_arg": "args[0]"},
                    "operations": {
                        "op1": {
                            "returns": "result",
                            "steps": ['echo "{{first_arg}}" => result'],
                        },
                        "op2": {
                            "returns": "result",
                            "steps": ['echo "{{first_arg}}" => result'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        cmd.args = ["shared-arg"]
        server = cmd.create_server()

        async def run_test():
            
            # Call first operation
            result1 = await mcp_call_tool(server, "op1", {})
            content1 = result1.content[0]
            data1 = json.loads(content1.text)
            self.assertEqual(data1["result"], "shared-arg")
            
            # Call second operation - should have same args
            result2 = await mcp_call_tool(server, "op2", {})
            content2 = result2.content[0]
            data2 = json.loads(content2.text)
            self.assertEqual(data2["result"], "shared-arg")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_args_with_interface_operation(self):
        """Args should work alongside interface parameters"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "combine": {
                            "accepts": {
                                "name": {"type": "string"},
                            },
                            "expressions": {"suffix": "args[0]"},
                            "returns": "result",
                            "steps": ['echo "{{name}}-{{suffix}}" => result'],
                        }
                    }
                }
            }
        )

        cmd = McpCommand(a)
        cmd.args = ["suffix"]
        server = cmd.create_server()

        async def run_test():
            result = await mcp_call_tool(server, "combine", {"name": "prefix"})
            
            content = result.content[0]
            data = json.loads(content.text)
            self.assertIn("result", data)
            self.assertEqual(data["result"], "prefix-suffix")

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())
