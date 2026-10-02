from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestTemplateFormattingInExpressions(DyngleTestCase):

    def test_get_function_gets_data_value(self):
        """Test that get() retrieves values from the dataset"""
        y = {
            "dyngle": {
                "constants": {"x": "hello"},
                "operations": {
                    "a": {
                        "expressions": {"b": "get('x')"},
                        "steps": ["{{b}}"],
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["hello"])

    def test_get_function_with_dotted_path(self):
        """Test that get() works with dotted paths"""
        y = {
            "dyngle": {
                "constants": {"x": {"y": "world"}},
                "operations": {
                    "a": {
                        "expressions": {"b": "get('x.y')"},
                        "steps": ["{{b}}"],
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["world"])

    def test_format_function_basic_template(self):
        """Test format() with simple template"""
        y = {
            "dyngle": {
                "constants": {"n": "Bob"},
                "operations": {
                    "a": {
                        "expressions": {"b": "format('Hi {{n}}')"},
                        "steps": ["{{b}}"],
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["Hi Bob"])

    def test_format_function_with_multiple_values(self):
        """Test format() with multiple template placeholders"""
        y = {
            "dyngle": {
                "constants": {"x": "foo", "y": "bar"},
                "operations": {
                    "a": {
                        "expressions": {"b": "format('{{x}}-{{y}}')"},
                        "steps": ["{{b}}"],
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["foo-bar"])

    def test_format_function_with_expressions(self):
        """Test format() can reference other expressions"""
        y = {
            "dyngle": {
                "constants": {"x": "5"},
                "operations": {
                    "a": {
                        "expressions": {
                            "num": "int(x) * 2",
                            "msg": "format('Result: {{num}}')",
                        },
                        "steps": ["{{msg}}"],
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["Result: 10"])

    def test_format_and_get_together(self):
        """Test using both format() and get() in same expression"""
        y = {
            "dyngle": {
                "constants": {"a": {"b": "test"}},
                "operations": {
                    "op": {
                        "expressions": {
                            "msg": "format('Value: {{a.b}}') + ' - ' + get('a.b')"  # noqa: E501
                        },
                        "steps": ["{{msg}}"],
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["Value: test - test"])
