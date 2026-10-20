import asyncio
from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.command.mcp_command import McpCommand
from test import DyngleTestCase, mcp_call_tool


class TestMcpToolErrorsAsResults(DyngleTestCase):
    """Operation failures come back as error tool results (is_error=True),
    not as JSON-RPC protocol errors, so the calling model can see them."""

    def test_validation_failure_returns_error_result(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "greet": {
                            "accepts": {"count": {"type": "integer"}},
                            "returns": "msg",
                            "steps": ['echo "Count {{count}}" => msg'],
                        }
                    }
                }
            }
        )
        server = McpCommand(a).create_server()

        async def run_test():
            result = await mcp_call_tool(server, "greet", {})
            self.assertTrue(result.is_error)
            self.assertEqual(result.content[0].type, "text")
            self.assertIn("Input validation failed", result.content[0].text)
            self.assertIn("greet", result.content[0].text)

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())

    def test_successful_call_is_not_error(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "ok": {
                            "returns": "out",
                            "steps": ['echo "fine" => out'],
                        }
                    }
                }
            }
        )
        server = McpCommand(a).create_server()

        async def run_test():
            result = await mcp_call_tool(server, "ok")
            self.assertFalse(result.is_error)

        with self.patchout(), self.patcherr():
            asyncio.run(run_test())
