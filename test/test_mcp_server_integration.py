# import asyncio
# import json
# from wizlib.config_handler import ConfigHandler

# from mcp.client.session import ClientSession
# from mcp.client.stdio import StdioServerParameters, stdio_client

# from dyngle import DyngleApp
# from test import DyngleTestCase


# class TestMcpServerIntegration(DyngleTestCase):
#     """Integration tests that run actual client-server communication"""

#     def test_basic_operation_execution_via_client(self):
#         """Test that an MCP client can connect and execute operations"""
        
#         async def run_test():
#             # Set up server parameters to run dyngle mcp command
#             server_params = StdioServerParameters(
#                 command="dyngle",
#                 args=["--config", "sandbox/simple.yml", "mcp"],
#                 env=None
#             )
            
#             async with stdio_client(server_params) as (read, write):
#                 async with ClientSession(read, write) as session:
#                     # Initialize the session
#                     await session.initialize()
                    
#                     # List tools
#                     tools_result = await session.list_tools()
#                     tool_names = [t.name for t in tools_result.tools]
                    
#                     # Verify we got some tools
#                     self.assertGreater(len(tool_names), 0)
                    
#                     # If there's an echo-like operation, test it
#                     if any('simple' in name.lower() for name in tool_names):
#                         return  # Just verify connection worked
        
#         with self.patchout(), self.patcherr():
#             asyncio.run(run_test())

#     def test_client_can_call_tool_with_parameters(self):
#         """Test calling a tool with input parameters through client"""
        
#         async def run_test():
#             server_params = StdioServerParameters(
#                 command="dyngle",
#                 args=["--config", "sandbox/simple.yml", "mcp"],
#                 env=None
#             )
            
#             async with stdio_client(server_params) as (read, write):
#                 async with ClientSession(read, write) as session:
#                     await session.initialize()
                    
#                     # List tools to see what's available
#                     tools_result = await session.list_tools()
                    
#                     if len(tools_result.tools) > 0:
#                         # Try calling the first tool
#                         tool = tools_result.tools[0]
#                         result = await session.call_tool(tool.name, {})
                        
#                         # Verify we got a response
#                         self.assertIsNotNone(result)
        
#         with self.patchout(), self.patcherr():
#             asyncio.run(run_test())
