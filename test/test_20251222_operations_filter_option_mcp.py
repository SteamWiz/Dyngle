import asyncio
import json
import tempfile
from pathlib import Path
from wizlib.config_handler import ConfigHandler
from mcp.types import ListToolsRequest, CallToolRequest

from dyngle import DyngleApp
from dyngle.command.mcp_command import McpCommand
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestOperationsFilterOptionMcp(DyngleTestCase):

    def test_operations_option_filters_to_single_operation(self):
        """--operations option should filter to specified operations"""
        y = """
dyngle:
  operations:
    op1:
      description: First operation
      steps:
        - echo "op1"
    op2:
      description: Second operation
      steps:
        - echo "op2"
    op3:
      description: Third operation
      steps:
        - echo "op3"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = "op2"
            server = cmd.create_server()

            async def run_test():
                handler = server.request_handlers[ListToolsRequest]
                result = await handler(ListToolsRequest())
                tools = result.root.tools
                
                # Should only have op2
                self.assertEqual(len(tools), 1)
                self.assertEqual(tools[0].name, "op2")

            asyncio.run(run_test())
        finally:
            Path(config_file).unlink()

    def test_operations_option_filters_to_multiple_operations(self):
        """--operations with comma-separated list filters to multiple ops"""
        y = """
dyngle:
  operations:
    alpha:
      steps: ['echo "a"']
    beta:
      steps: ['echo "b"']
    gamma:
      steps: ['echo "c"']
    delta:
      steps: ['echo "d"']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = "alpha,gamma"
            server = cmd.create_server()

            async def run_test():
                handler = server.request_handlers[ListToolsRequest]
                result = await handler(ListToolsRequest())
                tools = result.root.tools
                tool_names = [t.name for t in tools]
                
                # Should only have alpha and gamma
                self.assertEqual(len(tools), 2)
                self.assertIn("alpha", tool_names)
                self.assertIn("gamma", tool_names)
                self.assertNotIn("beta", tool_names)
                self.assertNotIn("delta", tool_names)

            asyncio.run(run_test())
        finally:
            Path(config_file).unlink()

    def test_operations_option_fails_with_invalid_key(self):
        """--operations with invalid key should raise error"""
        y = """
dyngle:
  operations:
    valid:
      steps: ['echo "test"']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = "invalid"
            
            # Should raise DyngleError
            with self.assertRaises(DyngleError) as ctx:
                cmd.create_server()
            
            self.assertIn("invalid", str(ctx.exception))
        finally:
            Path(config_file).unlink()

    def test_operations_option_fails_with_one_invalid_in_list(self):
        """--operations with one invalid key in list should raise error"""
        y = """
dyngle:
  operations:
    op1:
      steps: ['echo "1"']
    op2:
      steps: ['echo "2"']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = "op1,nonexistent,op2"
            
            # Should raise DyngleError
            with self.assertRaises(DyngleError) as ctx:
                cmd.create_server()
            
            self.assertIn("nonexistent", str(ctx.exception))
        finally:
            Path(config_file).unlink()

    def test_operations_option_none_shows_all_operations(self):
        """When --operations is not specified, all operations show"""
        y = """
dyngle:
  operations:
    op1:
      steps: ['echo "1"']
    op2:
      steps: ['echo "2"']
    op3:
      steps: ['echo "3"']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            # operations not set - should default to None
            server = cmd.create_server()

            async def run_test():
                handler = server.request_handlers[ListToolsRequest]
                result = await handler(ListToolsRequest())
                tools = result.root.tools
                tool_names = [t.name for t in tools]
                
                # Should have all three operations
                self.assertEqual(len(tools), 3)
                self.assertIn("op1", tool_names)
                self.assertIn("op2", tool_names)
                self.assertIn("op3", tool_names)

            asyncio.run(run_test())
        finally:
            Path(config_file).unlink()

    def test_filtered_operation_can_be_called(self):
        """Filtered operations should still be callable"""
        y = """
dyngle:
  operations:
    op1:
      returns: result
      steps:
        - echo "op1-result" => result
    op2:
      returns: result
      steps:
        - echo "op2-result" => result
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = "op1"
            server = cmd.create_server()

            async def run_test():
                handler = server.request_handlers[CallToolRequest]
                result = await handler(
                    CallToolRequest(
                        params={"name": "op1", "arguments": {}}
                    )
                )
                
                content = result.root.content[0]
                data = json.loads(content.text)
                self.assertIn("result", data)
                self.assertEqual(data["result"], "op1-result")

            with self.patchout(), self.patcherr():
                asyncio.run(run_test())
        finally:
            Path(config_file).unlink()

    def test_operations_filter_respects_private_access(self):
        """Filter should still respect private access"""
        y = """
dyngle:
  operations:
    public-op:
      steps: ['echo "public"']
    private-op:
      access: private
      steps: ['echo "private"']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = "public-op,private-op"
            server = cmd.create_server()

            async def run_test():
                handler = server.request_handlers[ListToolsRequest]
                result = await handler(ListToolsRequest())
                tools = result.root.tools
                tool_names = [t.name for t in tools]
                
                # Should only have public-op
                self.assertEqual(len(tools), 1)
                self.assertIn("public-op", tool_names)
                self.assertNotIn("private-op", tool_names)

            asyncio.run(run_test())
        finally:
            Path(config_file).unlink()

    def test_operations_option_with_whitespace(self):
        """--operations should handle whitespace around commas"""
        y = """
dyngle:
  operations:
    op1:
      steps: ['echo "1"']
    op2:
      steps: ['echo "2"']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = "op1 , op2"
            server = cmd.create_server()

            async def run_test():
                handler = server.request_handlers[ListToolsRequest]
                result = await handler(ListToolsRequest())
                tools = result.root.tools
                tool_names = [t.name for t in tools]
                
                # Should have both operations
                self.assertEqual(len(tools), 2)
                self.assertIn("op1", tool_names)
                self.assertIn("op2", tool_names)

            asyncio.run(run_test())
        finally:
            Path(config_file).unlink()

    def test_operations_empty_string_shows_all(self):
        """Empty string for --operations should show all operations"""
        y = """
dyngle:
  operations:
    op1:
      steps: ['echo "1"']
    op2:
      steps: ['echo "2"']
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(y)
            f.flush()
            config_file = f.name

        try:
            a = DyngleApp()
            a.config = ConfigHandler.setup(config_file)

            cmd = McpCommand(a)
            cmd.operations = ""
            server = cmd.create_server()

            async def run_test():
                handler = server.request_handlers[ListToolsRequest]
                result = await handler(ListToolsRequest())
                tools = result.root.tools
                
                # Should have all operations
                self.assertEqual(len(tools), 2)

            asyncio.run(run_test())
        finally:
            Path(config_file).unlink()
