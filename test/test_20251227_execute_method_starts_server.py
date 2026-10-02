from test import DyngleTestCase
from dyngle import DyngleApp
from wizlib.config_handler import ConfigHandler
from dyngle.command.mcp_command import McpCommand

class TestMcpCommandExecution(DyngleTestCase):
    """Tests for McpCommand.execute() that require async handling"""

    def test_execute_method_starts_server(self):
        """Test that execute() method starts the MCP server"""
        from unittest.mock import patch, AsyncMock, MagicMock

        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "test": {"steps": ['echo "test"']},
                    }
                }
            }
        )

        cmd = McpCommand(a)
        cmd.transport = "stdio"

        # Create a mock server with async run method
        mock_server = MagicMock()
        mock_server.run = AsyncMock()
        mock_server.create_initialization_options = MagicMock(return_value={})

        # Patch create_server to return our mock server
        with patch.object(cmd, 'create_server', return_value=mock_server):
            # Mock stdio_server context manager
            with patch('mcp.server.stdio.stdio_server') as mock_stdio:
                mock_stdio.return_value.__aenter__.return_value = (
                    AsyncMock(),  # read_stream
                    AsyncMock()   # write_stream
                )
                mock_stdio.return_value.__aexit__.return_value = None

                cmd.execute()

                # Verify server.run was called
                mock_server.run.assert_called_once()

                # Verify status was set
                self.assertIn("MCP server started", cmd.status)
                self.assertIn("stdio", cmd.status)
