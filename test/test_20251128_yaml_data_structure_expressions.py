from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestYamlDataStructureExpressions(DyngleTestCase):

    def test_simple_dict_structure(self):
        """Test that a YAML mapping is converted to a dict expression"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {
                            "info": {
                                "name": "'Alice'",
                                "age": "30"
                            }
                        },
                        "steps": ["{{info.name}} {{info.age}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["Alice", "30"])

    def test_simple_list_structure(self):
        """Test that a YAML sequence is converted to a list expression"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {
                            "coords": [
                                "10",
                                "20",
                                "30"
                            ],
                            "first": "get('coords')[0]",
                            "second": "get('coords')[1]"
                        },
                        "steps": ["{{first}} {{second}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["10", "20"])

    def test_nested_structure(self):
        """Test nested dicts and lists"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {
                            "data": {
                                "user": {
                                    "name": "'Bob'",
                                    "email": "'bob@example.com'"
                                },
                                "scores": [
                                    "95",
                                    "87",
                                    "92"
                                ]
                            },
                            "first-score": "get('data')['scores'][0]"
                        },
                        "steps": [
                            "{{data.user.name}}",
                            "{{first-score}}"
                        ]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        # First step outputs Bob
        self.assertEqual(p.call_args_list[0].args[0], ["Bob"])
        # Second step outputs 95
        self.assertEqual(p.call_args_list[1].args[0], ["95"])

    def test_expressions_with_get_function(self):
        """Test using get() within YAML structures"""
        y = {
            "dyngle": {
                "constants": {
                    "first": "John",
                    "last": "Doe"
                },
                "operations": {
                    "a": {
                        "expressions": {
                            "full": {
                                "name": "get('first') + ' ' + get('last')",
                                "length": "len(get('first'))"
                            }
                        },
                        "steps": ["{{full.name}} {{full.length}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["John Doe", "4"])

    def test_expressions_with_format_function(self):
        """Test using format() within YAML structures"""
        y = {
            "dyngle": {
                "constants": {
                    "city": "Seattle",
                    "state": "WA"
                },
                "operations": {
                    "a": {
                        "expressions": {
                            "location": {
                                "full": "format('{{city}}, {{state}}')",
                                "short": "format('{{city}}')"
                            }
                        },
                        "steps": ["{{location.full}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["Seattle, WA"])

    def test_backward_compatibility_string_expressions(self):
        """Test that string-based expressions still work"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {
                            "old": "{'key': 'value'}",
                            "new": {
                                "key": "'value'"
                            }
                        },
                        "steps": [
                            "{{old.key}}",
                            "{{new.key}}"
                        ]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["value"])
        self.assertEqual(p.call_args_list[1].args[0], ["value"])

    def test_global_yaml_expressions(self):
        """Test YAML structure expressions at global level"""
        y = {
            "dyngle": {
                "expressions": {
                    "config": {
                        "timeout": "30",
                        "retries": "3"
                    }
                },
                "operations": {
                    "a": {
                        "steps": ["{{config.timeout}} {{config.retries}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["30", "3"])

    def test_list_with_expressions(self):
        """Test list containing expressions that reference other values"""
        y = {
            "dyngle": {
                "constants": {
                    "base": 10
                },
                "operations": {
                    "a": {
                        "expressions": {
                            "multiples": [
                                "get('base') * 1",
                                "get('base') * 2",
                                "get('base') * 3"
                            ],
                            "middle": "get('multiples')[1]"
                        },
                        "steps": ["{{middle}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["20"])

    def test_deeply_nested_structure(self):
        """Test deeply nested structures (4+ levels)"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {
                            "deep": {
                                "level1": {
                                    "level2": {
                                        "level3": {
                                            "value": "'found'"
                                        }
                                    }
                                }
                            }
                        },
                        "steps": ["{{deep.level1.level2.level3.value}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["found"])

    def test_mixed_list_and_dict(self):
        """Test lists containing dicts and dicts containing lists"""
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {
                            "products": [
                                {
                                    "name": "'Apple'",
                                    "price": "1.50"
                                },
                                {
                                    "name": "'Banana'",
                                    "price": "0.75"
                                }
                            ],
                            "apple": "get('products')[0]"
                        },
                        "steps": [
                            "{{apple.name}} {{apple.price}}"
                        ]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        # Numeric expressions evaluate to their numeric type then stringify
        self.assertEqual(c, ["Apple", "1.5"])

    # def test_literal_values_in_yaml_structure(self):
    #     """Test that literal values (numbers, booleans, None) pass through"""
    #     y = {
    #         "dyngle": {
    #             "operations": {
    #                 "a": {
    #                     "expressions": {
    #                         "data": {
    #                             "count": 42,
    #                             "active": True,
    #                             "inactive": False,
    #                             "empty": None
    #                         }
    #                     },
    #                     "steps": ["{{data.count}} {{data.active}}"]
    #                 }
    #             }
    #         }
    #     }
    #     with NamedTemporaryFile(mode="w+") as f:
    #         safe_dump(y, f)
    #         f.seek(0)
    #         with self.patchout() as o, self.patcherr() as e, \
    #                 self.mock_subprocess_runner() as p:
    #             DyngleApp.start("--config", f.name, "run", "a", debug=True)
    #     c = p.call_args.args[0]
    #     # Literal values pass through unchanged
    #     self.assertEqual(c, ["42", "."])

    def test_yaml_expression_called_without_data(self):
        """Test error handling when yaml expression called without data"""
        from dyngle.model.expression import expression_structure
        from dyngle.error import DyngleError
        
        expr = expression_structure({"key": "'value'"})
        with self.assertRaises(DyngleError) as ctx:
            expr()
        self.assertIn("Expression called with no argument", str(ctx.exception))

    def test_non_standard_expression_type(self):
        """Test handling of non-standard expression types (edge case)"""
        # This tests the else clause in parse_constants that handles
        # unexpected types by converting them to strings
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {
                            # This will be parsed as an integer by YAML
                            "weird": 123
                        },
                        "steps": ["{{weird}}"]
                    }
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        # Integer gets converted to string then evaluated as "123"
        self.assertEqual(c, ["123"])
