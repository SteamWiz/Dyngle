import tracemalloc
tracemalloc.start()

from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestEmbeddedSchemaOperationInput(DyngleTestCase):

    def test_valid_data_passes_validation(self):
        """Valid data should pass interface validation"""
        y = {
            "dyngle": {
                "operations": {
                    "greet": {
                        "accepts": {"name": {"type": "string"}},
                        "steps": ['echo "Hello {{name}}"'],
                    }
                }
            }
        }
        d = {"name": "Alice"}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e:
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name, 
                    "run", "greet", debug=True
                )
            self.assertIn("Hello Alice", t.captured)

    def test_invalid_data_fails_validation(self):
        """Invalid data should fail interface validation"""
        y = {
            "dyngle": {
                "operations": {
                    "greet": {
                        "accepts": {
                            "name": {"type": "string", "required": True}
                        },
                        "steps": ['echo "Hello {{name}}"'],
                    }
                }
            }
        }
        d = {"age": 30}  # Missing required 'name'
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.assertRaises(DyngleError) as ctx:
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "greet", debug=True
                )
            self.assertIn("Input validation failed", str(ctx.exception))
            self.assertIn("required", str(ctx.exception).lower())

    def test_nested_object_validation(self):
        """Interface validation should work with nested objects"""
        y = {
            "dyngle": {
                "operations": {
                    "info": {
                        "accepts": {
                            "user": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "age": {"type": "integer"},
                                },
                                "required": ["name"],
                            }
                        },
                        "steps": ['echo "{{user.name}} is {{user.age}}"'],
                    }
                }
            }
        }
        d = {"user": {"name": "Bob", "age": 25}}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e:
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "info", debug=True
                )
            self.assertIn("Bob is 25", t.captured)

    def test_array_validation(self):
        """Interface validation should work with arrays"""
        y = {
            "dyngle": {
                "operations": {
                    "process": {
                        "accepts": {
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 1,
                            }
                        },
                        "steps": ['echo "Count: 3"'],
                    }
                }
            }
        }
        d = {"items": ["a", "b", "c"]}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e:
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "process", debug=True
                )
            self.assertIn("Count: 3", t.captured)

    def test_subop_valid_input_passes_validation(self):
        """Sub-operation with valid input: data should pass validation"""
        y = {
            "dyngle": {
                "operations": {
                    "child": {
                        "accepts": {"name": {"type": "string"}},
                        "steps": ['echo "Hello {{name}}"'],
                    },
                    "parent": {
                        "constants": {"data": {"name": "Charlie"}},
                        "steps": [{"sub": "child", "send": "data"}],
                    },
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start(
                    "--config", f.name, "run", "parent", debug=True
                )
            self.assertIn("Hello Charlie", t.captured)

    def test_subop_invalid_input_fails_validation(self):
        """Sub-operation with invalid input: data should fail validation"""
        y = {
            "dyngle": {
                "operations": {
                    "child": {
                        "accepts": {
                            "name": {"type": "string", "required": True}
                        },
                        "steps": ['echo "Hello {{name}}"'],
                    },
                    "parent": {
                        "constants": {"data": {"age": 30}},
                        "steps": [{"sub": "child", "send": "data"}],
                    },
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.patch_stream(""), self.assertRaises(
                        DyngleError
                    ) as ctx:
                DyngleApp.start(
                    "--config", f.name, "run", "parent", debug=True
                )
            self.assertIn("Input validation failed", str(ctx.exception))
            self.assertIn("required", str(ctx.exception).lower())

    def test_operation_without_interface_works_normally(self):
        """Operations without interface should work as before"""
        y = {
            "dyngle": {
                "operations": {
                    "greet": ["echo \"Hello {{name}}\""]
                }
            }
        }
        d = {"name": "Dave"}
        with NamedTemporaryFile(mode="w+") as cf, NamedTemporaryFile(
            mode="w+"
        ) as df:
            safe_dump(y, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e:
                DyngleApp.start(
                    "--config", cf.name, "--stream", df.name,
                    "run", "greet", debug=True
                )
            self.assertIn("Hello Dave", t.captured)
