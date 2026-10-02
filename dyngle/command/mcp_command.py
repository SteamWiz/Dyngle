from wizlib.parser import WizParser

from dyngle.command import DyngleCommand
from dyngle.servers.mcp_server import create_mcp_server, parse_operations_filter


class McpCommand(DyngleCommand):
    """Run an MCP server exposing Dyngle operations as tools"""

    name = "mcp"

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument(
            "args", nargs="*", help="Optional arguments passed to all operations"
        )
        parser.add_argument(
            "--transport",
            default="stdio",
            choices=["stdio"],
            help="Transport protocol to use",
        )
        parser.add_argument(
            "--operations",
            default=None,
            help="Comma-separated list of operations to expose as tools",
        )


    def create_server(self):
        operations = self.app.toolset.operations
        operations_filter = None
        if hasattr(self, 'operations') and self.operations:
            operations_filter = parse_operations_filter(
                self.operations,
                operations
            )
        
        # Get args from command line, default to empty list
        args = getattr(self, 'args', [])
        
        server = create_mcp_server(operations, operations_filter, args)
        return server


    @DyngleCommand.wrap
    def execute(self):
        """Start the MCP server """
        server = self.create_server()
        from mcp.server.stdio import stdio_server
        import asyncio
        async def run_server():  # pragma: nocover
            async with stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options()
                )        
        asyncio.run(run_server())
        # No-op
        self.status = f"MCP server started on {self.transport}"
