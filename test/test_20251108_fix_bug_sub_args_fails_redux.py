from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestSubOperationArgsScoping(DyngleTestCase):

    def test_parent_args_restored_after_sub_operation(self):
        """Test that parent's args are restored after calling a
        sub-operation"""
        y = {
            "dyngle": {
                "operations": {
                    "helper": {"steps": ['echo "helper called" => h']},
                    "parent-with-arg": {
                        "expressions": {"arg_value": "args[0]"},
                        "steps": [{"sub": "helper"}, "echo {{arg_value}} => p"],
                    },
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start(
                    "--config",
                    f.name,
                    "run",
                    "parent-with-arg",
                    "test-value",
                    debug=True,
                )
        # stdout is captured to variables, so trap should be empty
        self.assertEqual(t.captured, "")

    def test_nested_sub_operations_restore_args(self):
        """Test that nested sub-operations restore parent's args at each
        level"""
        y = {
            "dyngle": {
                "operations": {
                    "inner-helper": {"steps": ['echo "inner helper" => i']},
                    "middle-helper": {
                        "steps": [
                            {"sub": "inner-helper"},
                            'echo "middle helper" => m',
                        ]
                    },
                    "outer-with-arg": {
                        "expressions": {"my_arg": "args[0]"},
                        "steps": [
                            {"sub": "middle-helper"},
                            'echo "arg is {{my_arg}}" => o',
                        ],
                    },
                }
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, \
                    self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start(
                    "--config",
                    f.name,
                    "run",
                    "outer-with-arg",
                    "preserved",
                    debug=True,
                )
        # stdout is captured to variables, so trap should be empty
        self.assertEqual(t.captured, "")

    # def test_sub_operation_args_do_not_leak_to_parent(self):
    #     """Test that sub-operation's args don't affect parent after return"""
    #     y = {
    #         "dyngle": {
    #             "operations": {
    #                 "sub-with-different-arg": {
    #                     "expressions": {"val": "args[0]"},
    #                     "steps": ['echo "sub sees {{val}}" => s'],
    #                 },
    #                 "parent-with-arg": {
    #                     "expressions": {"parent_val": "args[0]"},
    #                     "steps": [
    #                         'echo "parent has {{parent_val}}" => p1',
    #                         {
    #                             "sub": "sub-with-different-arg",
    #                             "args": ["sub-arg"],
    #                         },
    #                         'echo "parent still has {{parent_val}}" => p2',
    #                     ],
    #                 },
    #             }
    #         }
    #     }
    #     with NamedTemporaryFile(mode="w+") as f:
    #         safe_dump(y, f)
    #         f.seek(0)
    #         with self.subprocess_runner_trap() as t, \
    #                 self.patchout() as o, self.patcherr() as e, self.patch_stream(""):
    #             DyngleApp.start(
    #                 "--config",
    #                 f.name,
    #                 "run",
    #                 "parent-with-arg",
    #                 "parent-arg",
    #                 debug=True,
    #             )
    #     # stdout is captured to variables, so trap should be empty
    #     self.assertEqual(t.captured, "")
