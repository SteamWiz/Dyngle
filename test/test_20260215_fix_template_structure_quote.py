from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestTemplateStructureQuoteHandling(DyngleTestCase):

    def test_template_with_single_quote(self):
        """Test templates handle strings with single quotes"""
        y = {
            "dyngle": {
                "templates": {"t": "It's working"},
                "operations": {
                    "op": {
                        "expressions": {"r": "get('t')"},
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, ["It's working"])

    def test_template_with_double_quote(self):
        """Test templates handle strings with double quotes"""
        y = {
            "dyngle": {
                "templates": {"t": 'He said "hello"'},
                "operations": {
                    "op": {
                        "expressions": {"r": "get('t')"},
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, ['He said "hello"'])

    def test_template_with_both_quotes(self):
        """Test templates handle strings with both quote types"""
        y = {
            "dyngle": {
                "templates": {"t": """It's "great" to work"""},
                "operations": {
                    "op": {
                        "expressions": {"r": "get('t')"},
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, ["""It's "great" to work"""])

    def test_template_with_multiline_text(self):
        """Test templates handle multiline strings"""
        t = """Line one
Line two
Line three"""
        y = {
            "dyngle": {
                "templates": {"t": t},
                "operations": {
                    "op": {
                        "expressions": {"r": "get('t')"},
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, [t])

    def test_template_with_python_code(self):
        """Test templates handle strings containing Python code"""
        t = """def foo():
    return 'hello' + "world"
    '''triple single'''
    \"\"\"triple double\"\"\""""
        y = {
            "dyngle": {
                "templates": {"t": t},
                "operations": {
                    "op": {
                        "expressions": {"r": "get('t')"},
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, [t])

    def test_template_with_backslashes(self):
        """Test templates handle strings with backslashes"""
        y = {
            "dyngle": {
                "templates": {"t": r"C:\path\to\file"},
                "operations": {
                    "op": {
                        "expressions": {"r": "get('t')"},
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, [r"C:\path\to\file"])

    def test_template_dict_with_quotes(self):
        """Test templates with dict containing quoted strings"""
        y = {
            "dyngle": {
                "constants": {"n": "Alice"},
                "templates": {
                    "d": {
                        "a": "It's {{n}}",
                        "b": 'Say "hi"',
                    }
                },
                "operations": {
                    "op": {
                        "expressions": {
                            "r": "get('d')['a'] + ' ' + get('d')['b']"
                        },
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, ["It's Alice Say \"hi\""])

    def test_template_list_with_quotes(self):
        """Test templates with list containing quoted strings"""
        y = {
            "dyngle": {
                "templates": {
                    "l": ["It's fine", 'Say "hello"']
                },
                "operations": {
                    "op": {
                        "expressions": {"r": "' | '.join(get('l'))"},
                        "steps": ["{{r}}"],
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
        self.assertEqual(c, ["It's fine | Say \"hello\""])
