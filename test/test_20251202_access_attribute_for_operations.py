from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestAccessAttributeForOperations(DyngleTestCase):

    def test_public_operation_can_be_run_directly(self):
        """Public operations (default) can be run via run command"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {"steps": ["echo test"]}
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "test"])

    def test_explicit_public_operation_can_be_run_directly(self):
        """Operations with access: public can be run via run command"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {"access": "public", "steps": ["echo test"]}
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "test"])

    def test_private_operation_cannot_be_run_directly(self):
        """Private operations cannot be run via run command"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {"access": "private", "steps": ["echo test"]}
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                with self.assertRaises(SystemExit):
                    DyngleApp.start("--config", f.name, "run", "a")
        # Check error message in stderr
        err = e.getvalue().lower()
        self.assertIn("private", err)

    def test_private_operation_can_be_called_as_suboperation(self):
        """Private operations can be called as sub-operations"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {"steps": [{"sub": "b"}]},
                    "b": {"access": "private", "steps": ["echo test"]}
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "test"])

    def test_list_operations_shows_only_public_operations(self):
        """list-operations command shows only public operations"""
        y = {
            "dyngle": {
                "operations": {
                    "public1": {"description": "Public op 1", "steps": []},
                    "public2": {
                        "access": "public",
                        "description": "Public op 2",
                        "steps": []
                    },
                    "private1": {
                        "access": "private",
                        "description": "Private op",
                        "steps": []
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e:
                DyngleApp.start("--config", f.name, "list-operations")
        output = o.getvalue()
        self.assertIn("public1", output)
        self.assertIn("public2", output)
        self.assertNotIn("private1", output)

    def test_invalid_access_value_raises_error(self):
        """Invalid access values should raise an error"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {"access": "invalid", "steps": ["echo test"]}
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e:
                with self.assertRaises(SystemExit):
                    DyngleApp.start("--config", f.name, "run", "a")
        err_msg = e.getvalue().lower()
        self.assertIn("invalid", err_msg)
        self.assertIn("access", err_msg)

    def test_mcp_server_exposes_only_public_operations(self):
        """MCP server exposes only public operations as tools"""
        import asyncio
        from mcp.types import ListToolsRequest
        from wizlib.config_handler import ConfigHandler
        from dyngle import DyngleApp
        from dyngle.command.mcp_command import McpCommand
        
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {
                        "public_op": {"steps": ["echo test"]},
                        "private_op": {
                            "access": "private",
                            "steps": ["echo private"]
                        }
                    },
                }
            }
        )

        cmd = McpCommand(a)
        server = cmd.create_server()
        
        async def run_test():
            handler = server.request_handlers[ListToolsRequest]
            result = await handler(ListToolsRequest())
            tool_names = [t.name for t in result.root.tools]
            self.assertIn("public_op", tool_names)
            self.assertNotIn("private_op", tool_names)
        
        asyncio.run(run_test())
