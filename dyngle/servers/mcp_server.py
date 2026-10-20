"""MCP server operations for exposing Dyngle operations as tools"""

import json
from mcp.server import Server, ServerRequestContext
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)

from dyngle.model.context import Context
from dyngle.model.operation import OperationAccess
from dyngle.error import DyngleError


def create_mcp_server(operations: dict, operations_filter: set = None, args: list = None) -> Server:
    """Create and configure an MCP server with tools for each operation
    
    Args:
        operations: Dictionary of operation name -> Operation objects
        operations_filter: Optional set of operation names to expose (None = all public ops)
        args: Optional list of positional arguments to pass to all operations
    
    Returns:
        Configured MCP Server instance
    """
    session_args = args or []

    async def list_tools(
        ctx: ServerRequestContext, params: PaginatedRequestParams | None
    ) -> ListToolsResult:
        """List all public operations as MCP tools"""
        tools = []
        
        for op_name, operation in operations.items():
            # Skip private operations
            if operation.access != OperationAccess.PUBLIC:
                continue
            
            # Skip operations not in filter if filter is set
            if operations_filter and op_name not in operations_filter:
                continue
            
            # Create input schema
            if operation.interface:
                # Use Interface's JSON Schema conversion
                properties = operation.interface.to_json_schema()
                required = operation.interface.get_required_fields()
                
                input_schema = {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            else:
                # No interface - no parameters
                input_schema = {
                    "type": "object",
                    "properties": {},
                }
            
            # Create tool with metadata
            tool = Tool(
                name=op_name,
                description=operation.description or f"Execute {op_name} operation",
                input_schema=input_schema,
            )
            tools.append(tool)

        return ListToolsResult(tools=tools)

    async def call_tool(
        ctx: ServerRequestContext, params: CallToolRequestParams
    ) -> CallToolResult:
        """Execute a Dyngle operation, reporting errors as tool results"""
        try:
            text = run_operation(params.name, params.arguments or {})
        except Exception as error:
            # mcp v2 no longer converts handler exceptions into isError
            # results; do it here so the calling model still sees the error.
            return CallToolResult(
                content=[TextContent(type="text", text=str(error))],
                is_error=True,
            )
        return CallToolResult(content=[TextContent(type="text", text=text)])

    def run_operation(name: str, arguments: dict) -> str:
        """Run the named operation and return its JSON-encoded result"""
        operation = operations.get(name)
        if not operation:  # pragma: nocover
            raise DyngleError(f"Unknown operation: {name}")
        
        # Prepare data and args based on interface
        if operation.interface_schema:
            # Interface present - all arguments become data
            data = arguments
        else:
            # No interface - no data
            data = {}
        
        # Add session args to data
        data['args'] = session_args
        
        # Create context from data
        context = Context(data)

        # Block stdout for MCP operations - results should come via return value
        return_value = operation.run(context, show_stdout=False)
        # Use default parameter to handle non-serializable types like Path objects
        return json.dumps({"result": return_value}, default=str)

    return Server(
        name="dyngle",
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )


def parse_operations_filter(operations_filter_str: str, operations: dict) -> set:
    """Parse and validate operations filter string
    
    Args:
        operations_filter_str: Comma-separated list of operation names
        operations: Dictionary of available operations
        
    Returns:
        Set of operation names to expose, or None if empty
        
    Raises:
        DyngleError: If any operation name in filter doesn't exist
    """
    if not operations_filter_str:  # pragma: nocover
        return None
        
    # Parse comma-separated list and strip whitespace
    op_list = [op.strip() for op in operations_filter_str.split(',')]
    # Filter out empty strings
    op_list = [op for op in op_list if op]
    
    if not op_list: # pragma: nocover
        return None
    
    # Validate all keys exist
    for op_key in op_list:
        if op_key not in operations:
            raise DyngleError(
                f"Operation '{op_key}' not found in toolset"
            )
    
    return set(op_list)
