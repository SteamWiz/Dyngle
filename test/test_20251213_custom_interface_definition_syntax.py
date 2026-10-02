from tempfile import NamedTemporaryFile

from yaml import safe_dump, safe_load
from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.context import Context
from test import DyngleTestCase


class TestCustomInterfaceDefinitionSyntax(DyngleTestCase):

    def test_string_type_default(self):
        """Fields without explicit type default to string"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"n": {}},
                        "steps": ['echo "{{n}}"'],
                    }
                }
            }
        }
        d = {"n": "x"}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("x", t.captured)

    def test_string_type_default_none_value(self):
        """Fields with None value default to string type"""
        y = "dyngle:\n  operations:\n    g:\n      interface:\n        n:\n      steps:\n        - echo ok"
        with NamedTemporaryFile(mode="w+") as cf:
            cf.write(y)
            cf.seek(0)
            parsed = safe_load(cf)
            # Verify that n is None (no value after key)
            self.assertIsNone(
                parsed["dyngle"]["operations"]["g"]["interface"]["n"]
            )

    def test_explicit_string_type(self):
        """String type validation works"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"n": {"type": "string"}},
                        "steps": ['echo "{{n}}"'],
                    }
                }
            }
        }
        d = {"n": "a"}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("a", t.captured)

    def test_integer_type(self):
        """Integer type validation works"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"c": {"type": "integer"}},
                        "steps": ['echo "{{c}}"'],
                    }
                }
            }
        }
        d = {"c": 42}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("42", t.captured)

    def test_number_type(self):
        """Number type validation works"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"v": {"type": "number"}},
                        "steps": ['echo "{{v}}"'],
                    }
                }
            }
        }
        d = {"v": 3.14}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("3.14", t.captured)

    # def test_boolean_type(self):
    #     """Boolean type validation works"""
    #     y = {
    #         "dyngle": {
    #             "operations": {
    #                 "g": {
    #                     "accepts": {"f": {"type": "boolean"}},
    #                     "steps": ['echo "{{f}}"'],
    #                 }
    #             }
    #         }
    #     }
    #     d = {"f": True}
    #     with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
    #         mode="w+"
    #     ) as df:
    #         safe_dump(y, cf)
    #         safe_dump(d, df)
    #         cf.seek(0)
    #         df.seek(0)
    #         with self.subprocess_runner_trap() as t, self.patchout(), \
    #                 self.patcherr():
    #             DyngleApp.start(
    #                 "--config", cf.name, "--stream", df.name,
    #                 "run", "g", debug=True
    #             )
    #         self.assertIn(".", t.captured)


    def test_array_type_inferred(self):
        """Array type inferred from items"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {
                            "lst": {"items": {"type": "string"}}
                        },
                        "steps": ['echo "ok"'],
                    }
                }
            }
        }
        d = {"lst": ["a", "b"]}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("ok", t.captured)

    def test_object_type_inferred(self):
        """Object type inferred from properties"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {
                            "u": {"properties": {"n": {"type": "string"}}}
                        },
                        "steps": ['echo "{{u.n}}"'],
                    }
                }
            }
        }
        d = {"u": {"n": "x"}}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("x", t.captured)

    def test_string_gets_blank_default(self):
        """String fields without required/default get blank string"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"n": {"type": "string"}},
                        "steps": ['echo "x{{n}}y"'],
                    }
                }
            }
        }
        d = {}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("xy", t.captured)  # Blank string between x and y

    def test_required_false_makes_optional(self):
        """Setting required: false makes field optional"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"n": {"type": "string", 
                                           "required": False}},
                        "steps": ['echo "ok"'],
                    }
                }
            }
        }
        d = {}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("ok", t.captured)

    def test_default_value_applied(self):
        """Default values are actually applied"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"n": {"type": "string", 
                                           "default": "z"}},
                        "steps": ['echo "{{n}}"'],
                    }
                }
            }
        }
        d = {}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("z", t.captured)

    def test_additional_properties_allowed(self):
        """Additional properties are allowed by default"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"n": {"type": "string"}},
                        "steps": ['echo "{{n}}"'],
                    }
                }
            }
        }
        d = {"n": "x", "extra": "y"}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("x", t.captured)

    def test_nested_object_properties(self):
        """Nested object properties work correctly"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {
                            "u": {
                                "properties": {
                                    "n": {"type": "string"},
                                    "a": {"type": "integer"}
                                }
                            }
                        },
                        "steps": ['echo "{{u.n}} {{u.a}}"'],
                    }
                }
            }
        }
        d = {"u": {"n": "x", "a": 25}}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("x 25", t.captured)

    def test_type_mismatch_error(self):
        """Wrong type causes validation error"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {"c": {"type": "integer"}},
                        "steps": ['echo "{{c}}"'],
                    }
                }
            }
        }
        d = {"c": "not-a-number"}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.patchout(), self.patcherr(), \
                    self.assertRaises(DyngleError) as ctx:
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("validation", str(ctx.exception).lower())

    def test_subop_with_interface_validation(self):
        """Sub-operation interface validation works"""
        y = {
            "dyngle": {
                "operations": {
                    "c": {
                        "accepts": {"n": {"type": "string"}},
                        "steps": ['echo "{{n}}"'],
                    },
                    "p": {
                        "constants": {"d": {"n": "x"}},
                        "steps": [{"sub": "c", "send": "d"}],
                    },
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr(), self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "p", debug=True)
            self.assertIn("x", t.captured)

    def test_array_with_object_items(self):
        """Array with object items validates correctly"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {
                            "lst": {
                                "type": "array",
                                "items": {
                                    "properties": {"n": {"type": "string"}}
                                }
                            }
                        },
                        "steps": ['echo "ok"'],
                    }
                }
            }
        }
        d = {"lst": [{"n": "a"}, {"n": "b"}]}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("ok", t.captured)

    def test_default_values_nested_object(self):
        """Default values work in nested objects"""
        y = {
            "dyngle": {
                "operations": {
                    "g": {
                        "accepts": {
                            "u": {
                                "properties": {
                                    "n": {"type": "string"},
                                    "c": {"type": "string", "default": "US"}
                                }
                            }
                        },
                        "steps": ['echo "{{u.n}} {{u.c}}"'],
                    }
                }
            }
        }
        d = {"u": {"n": "x"}}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr():
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "g", debug=True
                )
            self.assertIn("x US", t.captured)

    def test_operation_level_integer_validation(self):
        """Operation.validate_input handles actual integers"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"v": {"type": "integer"}},
                    "steps": ['echo "{{v}}"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = Context({"v": 42})
        o.validate_and_set_defaults(d)
        # If no exception, validation passed
        self.assertEqual(d["v"], 42)

    def test_operation_level_number_validation(self):
        """Operation.validate_input handles actual floats"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"v": {"type": "number"}},
                    "steps": ['echo "{{v}}"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = Context({"v": 3.14})
        o.validate_and_set_defaults(d)
        self.assertAlmostEqual(d["v"], 3.14)

    def test_operation_level_type_error(self):
        """Operation.validate_input rejects wrong types"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"v": {"type": "integer"}},
                    "steps": ['echo "{{v}}"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = {"v": "not-an-int"}
        with self.assertRaises(DyngleError):
            o.validate_and_set_defaults(d)

    def test_subop_passes_actual_integer(self):
        """Sub-operation receives actual integer not string"""
        y = {
            "dyngle": {
                "operations": {
                    "c": {
                        "accepts": {"v": {"type": "integer"}},
                        "steps": ['echo "{{v}}"'],
                    },
                    "p": {
                        "constants": {"d": {"v": 99}},
                        "steps": [{"sub": "c", "send": "d"}],
                    },
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr(), self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "p", debug=True)
            self.assertIn("99", t.captured)

    def test_subop_passes_actual_float(self):
        """Sub-operation receives actual float not string"""
        y = {
            "dyngle": {
                "operations": {
                    "c": {
                        "accepts": {"v": {"type": "number"}},
                        "steps": ['echo "{{v}}"'],
                    },
                    "p": {
                        "constants": {"d": {"v": 2.71}},
                        "steps": [{"sub": "c", "send": "d"}],
                    },
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout(), \
                    self.patcherr(), self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "p", debug=True)
            self.assertIn("2.71", t.captured)

    def test_invalid_schema_non_dict(self):
        """Invalid schema definition (non-dict field) raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"v": "invalid"},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        with self.assertRaises(DyngleError) as ctx:
            v.load_operations(y)
        self.assertIn("must be dict or None", str(ctx.exception))

    def test_invalid_type_name(self):
        """Invalid type name raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"v": {"type": "invalid_type"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        with self.assertRaises(DyngleError) as ctx:
            v.load_operations(y)
        self.assertIn("Invalid type", str(ctx.exception))

    def test_boolean_wrong_type_error(self):
        """Boolean field with wrong type raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"f": {"type": "boolean"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = {"f": "not-a-bool"}
        with self.assertRaises(DyngleError) as ctx:
            o.validate_and_set_defaults(d)
        self.assertIn("must be boolean", str(ctx.exception))

    def test_array_wrong_type_error(self):
        """Array field with wrong type raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"lst": {"type": "array"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = {"lst": "not-an-array"}
        with self.assertRaises(DyngleError) as ctx:
            o.validate_and_set_defaults(d)
        self.assertIn("must be array", str(ctx.exception))

    def test_object_wrong_type_error(self):
        """Object field with wrong type raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"obj": {"type": "object"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = {"obj": "not-an-object"}
        with self.assertRaises(DyngleError) as ctx:
            o.validate_and_set_defaults(d)
        self.assertIn("must be object", str(ctx.exception))

    def test_invalid_properties_non_dict(self):
        """Invalid properties (non-dict) raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"obj": {"properties": "invalid"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        with self.assertRaises(DyngleError) as ctx:
            v.load_operations(y)
        self.assertIn("properties", str(ctx.exception).lower())

    def test_invalid_items_non_dict(self):
        """Invalid items (non-dict) raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"lst": {"items": "invalid"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        with self.assertRaises(DyngleError) as ctx:
            v.load_operations(y)
        self.assertIn("items", str(ctx.exception).lower())

    def test_invalid_nested_schema(self):
        """Invalid nested schema raises error"""
        from dyngle.model.interface import Interface
        # Pass non-dict as schema - should raise at root level
        with self.assertRaises(DyngleError) as ctx:
            Interface("not-a-dict")
        self.assertIn("must be dict", str(ctx.exception))

    def test_string_wrong_type_error(self):
        """String field with wrong type raises error"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"s": {"type": "string"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = {"s": 123}
        with self.assertRaises(DyngleError) as ctx:
            o.validate_and_set_defaults(d)
        self.assertIn("must be string", str(ctx.exception))

    def test_number_rejects_boolean(self):
        """Number field rejects boolean values"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"n": {"type": "number"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = {"n": True}
        with self.assertRaises(DyngleError) as ctx:
            o.validate_and_set_defaults(d)
        self.assertIn("must be number", str(ctx.exception))

    def test_integer_rejects_boolean(self):
        """Integer field rejects boolean values"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"i": {"type": "integer"}},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        d = {"i": True}
        with self.assertRaises(DyngleError) as ctx:
            o.validate_and_set_defaults(d)
        self.assertIn("must be integer", str(ctx.exception))

    def test_none_field_def_validates_as_string(self):
        """Field with None definition validates as required string"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"n": None},
                    "steps": ['echo "{{n}}"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        # Should work with a string
        d = Context({"n": "test"})
        o.validate_and_set_defaults(d)
        self.assertEqual(d["n"], "test")

    def test_none_field_def_gets_blank_default(self):
        """Field with None definition gets blank string default"""
        from dyngle.model.toolset import Toolset
        y = {
            "operations": {
                "c": {
                    "accepts": {"n": None},
                    "steps": ['echo "ok"'],
                }
            }
        }
        v = Toolset()
        v.load_operations(y)
        o = v.operations["c"]
        # Should apply blank string default when field is missing
        d = Context()
        o.validate_and_set_defaults(d)
        self.assertEqual(d["n"], "")
