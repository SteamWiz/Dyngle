from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestListIndexing(DyngleTestCase):
    """Test list indexing via dot notation in context.dig()"""

    def test_list_index_valid(self):
        """Test accessing list elements with valid numeric indices"""
        y = {
            "dyngle": {
                "constants": {"items": ["alpha", "beta", "gamma"]},
                "operations": {"op": {"steps": ["echo {{items.0}}", "echo {{items.1}}", "echo {{items.2}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        # Check that all three were called with correct values
        self.assertEqual(p.call_count, 3)
        calls = [call.args[0] for call in p.call_args_list]
        self.assertEqual(calls[0], ["echo", "alpha"])
        self.assertEqual(calls[1], ["echo", "beta"])
        self.assertEqual(calls[2], ["echo", "gamma"])

    def test_list_index_from_expression(self):
        """Test accessing list elements from an expression result"""
        y = {
            "dyngle": {
                "expressions": {"nums": "[10, 20, 30, 40]"},
                "operations": {"op": {"steps": ["{{nums.2}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["30"])

    def test_list_index_nested_access(self):
        """Test accessing nested structures through list indexing"""
        y = {
            "dyngle": {
                "expressions": {"data": "[{'name': 'first'}, {'name': 'second'}]"},
                "operations": {"op": {"steps": ["{{data.1.name}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["second"])

    def test_list_index_non_digit(self):
        """Test that non-digit list indices raise format error"""
        y = {
            "dyngle": {
                "constants": {"items": ["a", "b", "c"]},
                "operations": {"op": {"steps": ["{{items.abc}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.assertRaises(DyngleError) as ctx, self.patchout(), self.patcherr():
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        self.assertIn("Unresolvable key", 
                      str(ctx.exception))

    # def test_list_index_out_of_bounds(self):
    #     """Test that out of bounds indices raise format error"""
    #     y = {
    #         "dyngle": {
    #             "constants": {"items": ["x", "y"]},
    #             "operations": {"op": {"steps": ["{{items.5}}"]}},
    #         }
    #     }
    #     with NamedTemporaryFile(mode="w+") as f:
    #         safe_dump(y, f)
    #         f.seek(0)
    #         with self.assertRaises(DyngleError) as ctx:
    #             DyngleApp.start("--config", f.name, "run", "op", debug=True)
    #     self.assertIn("Unresolvable key", 
    #                   str(ctx.exception))

    # def test_list_index_equal_to_length(self):
    #     """Test that index equal to length is out of bounds"""
    #     y = {
    #         "dyngle": {
    #             "constants": {"items": ["a", "b"]},
    #             "operations": {"op": {"steps": ["{{items.2}}"]}},
    #         }
    #     }
    #     with NamedTemporaryFile(mode="w+") as f:
    #         safe_dump(y, f)
    #         f.seek(0)
    #         with self.assertRaises(DyngleError) as ctx:
    #             DyngleApp.start("--config", f.name, "run", "op", debug=True)
    #     self.assertIn("Unresolvable key", 
    #                   str(ctx.exception))

    def test_access_property_of_non_dict_non_list(self):
        """Test that accessing properties of strings raises format error"""
        y = {
            "dyngle": {
                "constants": {"value": "hello"},
                "operations": {"op": {"steps": ["{{value.length}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.assertRaises(DyngleError) as ctx, self.patchout(), self.patcherr():
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        self.assertIn("Unresolvable key", 
                      str(ctx.exception))

    def test_access_property_of_number(self):
        """Test that accessing properties of numbers raises format error"""
        y = {
            "dyngle": {
                "constants": {"num": 42},
                "operations": {"op": {"steps": ["{{num.property}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.assertRaises(DyngleError) as ctx, self.patchout(), self.patcherr():
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        self.assertIn("Unresolvable key", 
                      str(ctx.exception))

    def test_list_with_nested_lists(self):
        """Test accessing elements in nested lists"""
        y = {
            "dyngle": {
                "expressions": {"matrix": "[[1, 2, 3], [4, 5, 6], [7, 8, 9]]"},
                "operations": {"op": {"steps": ["{{matrix.1.2}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["6"])

    def test_list_index_with_leading_zeros(self):
        """Test that indices with leading zeros still work (they're digits)"""
        y = {
            "dyngle": {
                "constants": {"items": ["first", "second", "third"]},
                "operations": {"op": {"steps": ["{{items.01}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["second"])
