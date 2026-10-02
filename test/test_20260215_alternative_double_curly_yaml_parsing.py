from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestDollarSyntax(DyngleTestCase):

    def test_dollar_simple_constant(self):
        """$name should work like {{name}} for simple constants"""
        y = {
            "dyngle": {
                "constants": {"n": "Alice"},
                "operations": {"a": {"steps": ["echo $n"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "Alice"])

    def test_dollar_hyphenated_constant(self):
        """$first-name should work for hyphenated identifiers"""
        y = {
            "dyngle": {
                "constants": {"first-name": "Bob"},
                "operations": {"a": {"steps": ["echo $first-name"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "Bob"])

    def test_dollar_nested_property(self):
        """$server.host should work for nested properties"""
        y = {
            "dyngle": {
                "constants": {"server": {"host": "example.com"}},
                "operations": {"a": {"steps": ["echo $server.host"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "example.com"])

    def test_dollar_expression(self):
        """$expr should work with expressions"""
        y = {
            "dyngle": {
                "expressions": {"x": "'computed'"},
                "operations": {"a": {"steps": ["echo $x"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "computed"])

    def test_dollar_returns_python_type(self):
        """$var should return Python types like {{var}} does"""
        y = {
            "dyngle": {
                "constants": {"nums": [1, 2, 3]},
                "operations": {"a": {"steps": ["echo $nums"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", 1, 2, 3])

    def test_dollar_not_in_middle_of_string(self):
        """$var should not be replaced when part of a larger string"""
        y = {
            "dyngle": {
                "constants": {"n": "Alice"},
                "operations": {"a": {"steps": ["echo Hello$n"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "Hello$n"])

    def test_dollar_in_quotes_is_separate_word(self):
        """$var in quotes should still work as it's a separate word"""
        y = {
            "dyngle": {
                "constants": {"n": "Alice"},
                "operations": {"a": {"steps": ['echo "$n"']}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "Alice"])

    def test_dollar_and_curly_both_work(self):
        """Both $var and {{var}} should work in same template"""
        y = {
            "dyngle": {
                "constants": {"a": "A", "b": "B"},
                "operations": {"op": {"steps": ["echo $a {{b}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "A", "B"])

    def test_dollar_with_numeric_index(self):
        """$runtime.args.0 should work for numeric indices"""
        y = {
            "dyngle": {
                "operations": {"a": {"steps": ["echo $runtime.args.0"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", "test", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "test"])
