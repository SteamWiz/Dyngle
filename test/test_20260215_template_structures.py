from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.expression import template_structure
from test import DyngleTestCase


class TestTemplateStructures(DyngleTestCase):

    def test_simple_string_template(self):
        """Test that templates: wraps strings in format()"""
        y = {
            "dyngle": {
                "constants": {"n": "Alice"},
                "templates": {"g": "Hello {{n}}"},
                "operations": {"a": {"steps": ["{{g}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["Hello Alice"])

    def test_template_with_multiple_placeholders(self):
        """Test templates with multiple template placeholders"""
        y = {
            "dyngle": {
                "constants": {"x": "foo", "y": "bar"},
                "templates": {"t": "{{x}}-{{y}}"},
                "operations": {"a": {"steps": ["{{t}}"]}},
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

    def test_template_with_nested_property(self):
        """Test templates can reference nested properties"""
        y = {
            "dyngle": {
                "constants": {"u": {"n": "Bob"}},
                "templates": {"g": "Hi {{u.n}}"},
                "operations": {"a": {"steps": ["{{g}}"]}},
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

    def test_local_template(self):
        """Test templates defined within an operation"""
        y = {
            "dyngle": {
                "constants": {"n": "World"},
                "operations": {
                    "a": {
                        "templates": {"m": "Hello {{n}}!"},
                        "steps": ["{{m}}"],
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
        self.assertEqual(c, ["Hello World!"])

    def test_template_dict_structure(self):
        """Test templates with dict structure"""
        y = {
            "dyngle": {
                "constants": {"x": "val1", "y": "val2"},
                "templates": {"d": {"a": "{{x}}", "b": "{{y}}"}},
                "operations": {
                    "op": {
                        "expressions": {"r": "get('d')['a'] + '-' + get('d')['b']"},  # noqa: E501
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
        self.assertEqual(c, ["val1-val2"])

    def test_template_list_structure(self):
        """Test templates with list structure"""
        y = {
            "dyngle": {
                "constants": {"x": "a", "y": "b"},
                "templates": {"l": ["{{x}}", "{{y}}"]},
                "operations": {
                    "op": {
                        "expressions": {"r": "'-'.join(get('l'))"},
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
        self.assertEqual(c, ["a-b"])

    def test_template_nested_structure(self):
        """Test templates with nested dict/list structures"""
        y = {
            "dyngle": {
                "constants": {"x": "foo", "y": "bar"},
                "templates": {
                    "s": {
                        "items": ["{{x}}", "{{y}}"],
                        "msg": "Values: {{x}} and {{y}}",
                    }
                },
                "operations": {
                    "op": {
                        "expressions": {
                            "r": "get('s')['msg'] + ' ' + str(get('s')['items'])"  # noqa: E501
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
        self.assertEqual(c, ["Values: foo and bar ['foo', 'bar']"])

    def test_template_with_int_constant(self):
        """Test that int values in templates are treated as constants"""
        y = {
            "dyngle": {
                "templates": {"v": 42},
                "operations": {
                    "op": {
                        "expressions": {"r": "str(get('v'))"},
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
        self.assertEqual(c, ["42"])

    def test_template_with_bool_constant(self):
        """Test that bool values in templates are treated as constants"""
        y = {
            "dyngle": {
                "templates": {"v": True},
                "operations": {
                    "op": {
                        "expressions": {"r": "str(get('v'))"},
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
        self.assertEqual(c, ["True"])

    def test_template_with_float_constant(self):
        """Test that float values in templates are treated as constants"""
        y = {
            "dyngle": {
                "templates": {"v": 3.14},
                "operations": {
                    "op": {
                        "expressions": {"r": "str(get('v'))"},
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
        self.assertEqual(c, ["3.14"])

    def test_template_mixed_structure(self):
        """Test templates with mixed types in structure"""
        y = {
            "dyngle": {
                "constants": {"n": "test"},
                "templates": {
                    "m": {
                        "str": "{{n}}",
                        "num": 10,
                        "flag": False,
                    }
                },
                "operations": {
                    "op": {
                        "expressions": {
                            "r": "get('m')['str'] + '-' + str(get('m')['num']) + '-' + str(get('m')['flag'])"  # noqa: E501
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
        self.assertEqual(c, ["test-10-False"])

    def test_template_structure_no_context_error(self):
        """Test that template_structure raises error when called with no
        context"""
        t = template_structure("test")
        with self.assertRaises(DyngleError):
            t(None)
