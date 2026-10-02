from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.context import Context
from test import DyngleTestCase


class TestConditionalSteps(DyngleTestCase):
    """Test conditional step execution with if/then/else blocks"""

    def test_basic_conditional_true(self):
        """Test basic conditional with true condition"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"x": "True"},
                        "steps": [
                            {
                                "if": "x",
                                "then": ['echo "yes"'],
                                "else": ['echo "no"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "yes"])

    def test_basic_conditional_false(self):
        """Test basic conditional with false condition"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"x": "False"},
                        "steps": [
                            {
                                "if": "x",
                                "then": ['echo "yes"'],
                                "else": ['echo "no"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "no"])

    def test_conditional_without_else(self):
        """Test conditional without else block"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"x": "False"},
                        "steps": [
                            'echo "before"',
                            {"if": "x", "then": ['echo "yes"']},
                            'echo "after"'
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        # Should execute before and after, but not the conditional
        self.assertEqual(p.call_count, 2)
        self.assertEqual(p.call_args_list[0].args[0], ["echo", "before"])
        self.assertEqual(p.call_args_list[1].args[0], ["echo", "after"])

    def test_conditional_with_expression(self):
        """Test conditional using expression evaluation"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"check": "env == 'prod'"},
                        "steps": [
                            {
                                "if": "check",
                                "then": ['echo "production"'],
                                "else": ['echo "development"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            ctx = Context({"env": "prod"})
            a.toolset.operations["test"].run(ctx)
        
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "production"])

    def test_conditional_with_variable_from_previous_step(self):
        """Test conditional using variable captured from previous step"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"ok": "code == '200'"},
                        "steps": [
                            'echo "200" => code',
                            {
                                "if": "ok",
                                "then": ['echo "healthy"'],
                                "else": ['echo "unhealthy"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            p.return_value = 0, "200"
            a.toolset.operations["test"].run(Context())
        
        # Second call should be the conditional result
        c = p.call_args_list[1].args[0]
        self.assertEqual(c, ["echo", "healthy"])

    def test_conditional_with_sub_operations(self):
        """Test conditional with sub-operation steps"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "helper": ['echo "helper"'],
                    "test": {
                        "expressions": {"x": "True"},
                        "steps": [
                            {
                                "if": "x",
                                "then": [{"sub": "helper"}],
                                "else": ['echo "no"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "helper"])

    def test_nested_conditionals(self):
        """Test nested conditional blocks"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {
                            "x": "True",
                            "y": "True"
                        },
                        "steps": [
                            {
                                "if": "x",
                                "then": [
                                    {
                                        "if": "y",
                                        "then": ['echo "both"'],
                                        "else": ['echo "x only"']
                                    }
                                ],
                                "else": ['echo "neither"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "both"])

    def test_conditional_with_data_flow(self):
        """Test conditional with data flow operators"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"use_json": "True"},
                        "steps": [
                            'echo "data" => raw',
                            {
                                "if": "use_json",
                                "then": ['raw -> echo "json" => result'],
                                "else": ['raw -> echo "yaml" => result']
                            },
                            'echo "{{result}}"'
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            p.return_value = 0, "json"
            a.toolset.operations["test"].run(Context())
        
        # Third call should use the result variable
        self.assertEqual(p.call_count, 3)

    def test_conditional_missing_reference_error(self):
        """Test error when if: references non-existent value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "steps": [
                            {
                                "if": "nonexistent",
                                "then": ['echo "yes"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout(), self.patcherr(), \
                self.mock_subprocess_runner():
            with self.assertRaises(DyngleError):
                a.toolset.operations["test"].run(Context())

    def test_conditional_truthiness_empty_string(self):
        """Test truthiness conversion for empty string"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "constants": {"x": ""},
                        "steps": [
                            {
                                "if": "x",
                                "then": ['echo "yes"'],
                                "else": ['echo "no"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "no"])

    def test_conditional_truthiness_non_zero(self):
        """Test truthiness conversion for non-zero number"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "constants": {"x": 42},
                        "steps": [
                            {
                                "if": "x",
                                "then": ['echo "yes"'],
                                "else": ['echo "no"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "yes"])

    def test_conditional_variable_scope(self):
        """Test that variables from conditional blocks persist"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"x": "True"},
                        "steps": [
                            {
                                "if": "x",
                                "then": ['echo "value" => result'],
                                "else": ['echo "other" => result']
                            },
                            'echo "{{result}}"'
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            p.return_value = 0, "value"
            a.toolset.operations["test"].run(Context())
        
        # Second call should have access to result
        c = p.call_args_list[1].args[0]
        self.assertEqual(c, ["echo", "value"])

    def test_conditional_with_prompt_step(self):
        """Test conditional with prompt steps"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"x": "True"},
                        "steps": [
                            {
                                "if": "x",
                                "then": [
                                    {"prompt": "Enter: ", "receive": "input"}
                                ],
                                "else": ['echo "skip"']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout(), self.patcherr(), \
                self.mock_subprocess_runner():
            # Mock the UI handler
            a.ui.get_text = lambda p: "test"
            a.toolset.operations["test"].run(Context())

    def test_conditional_multiple_steps_in_then(self):
        """Test conditional with multiple steps in then block"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "expressions": {"x": "True"},
                        "steps": [
                            {
                                "if": "x",
                                "then": [
                                    'echo "step1"',
                                    'echo "step2"',
                                    'echo "step3"'
                                ]
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout() as o, self.patcherr(), \
                self.mock_subprocess_runner() as p:
            a.toolset.operations["test"].run(Context())
        
        self.assertEqual(p.call_count, 3)
        self.assertEqual(p.call_args_list[0].args[0], ["echo", "step1"])
        self.assertEqual(p.call_args_list[1].args[0], ["echo", "step2"])
        self.assertEqual(p.call_args_list[2].args[0], ["echo", "step3"])

    def test_conditional_with_return_value(self):
        """Test operation with conditional and return value"""
        a = DyngleApp()
        a.config = ConfigHandler.setup({
            "dyngle": {
                "operations": {
                    "test": {
                        "returns": "result",
                        "expressions": {"x": "True"},
                        "steps": [
                            {
                                "if": "x",
                                "then": ['echo "yes" => result'],
                                "else": ['echo "no" => result']
                            }
                        ]
                    }
                }
            }
        })
        
        with self.patchout(), self.patcherr(), \
                self.mock_subprocess_runner() as p:
            p.return_value = 0, "yes"
            result = a.toolset.operations["test"].run(Context())
        
        self.assertEqual(result, "yes")
