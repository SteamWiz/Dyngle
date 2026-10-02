from wizlib.config_handler import ConfigHandler

from dyngle import DyngleApp
from dyngle.error import DyngleError

from test import DyngleTestCase


class TestRunCommand(DyngleTestCase):

    def test_execute_single_task(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"test": ["echo {{value}}"]}}}
        )
        with self.patchout() as o, self.patcherr() as e, \
            self.mock_subprocess_runner() as p, self.patch_stream(
            "value: hello"
        ):
            a.parse_run("run", "test")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "hello"])

    def test_invalid_operation(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"test": ["echo {{value}}"]}}}
        )
        with self.patchout() as o, self.patcherr() as e, \
            self.mock_subprocess_runner() as p, self.patch_stream(
            "value: hello"
        ):
            with self.assertRaises(DyngleError):
                a.parse_run("run", "not")

    def test_operation_failure(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"test": ["bash -c 'exit 1'"]}}}
        )
        with self.patchout() as o, self.patcherr() as e:
            with self.assertRaises(DyngleError):
                a.parse_run("run", "test")

    def test_operations_with_expressions(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {"say": ["echo '{{hello}}'"]},
                    "expressions": {"hello": "'Hello '+name+'!'"},
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p, self.patch_stream(
            "name: A"
        ):
            a.parse_run("run", "say")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "Hello A!"])

    def test_expression_with_hyphen(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {"say": ["echo '{{hi-you}}'"]},
                    "expressions": {"hi-you": "'Hello '+name+'!'"},
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p, self.patch_stream(
            "name: A"
        ):
            a.parse_run("run", "say")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "Hello A!"])

    def test_run_with_extra_args(self):
        """First make sure it doesn't fail"""
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {"dyngle": {"operations": {"a": ["echo"]}}}
        )
        with self.patchout() as o, self.patcherr() as e, \
            self.mock_subprocess_runner() as p, self.patch_stream(
            "value: hello"
        ):
            a.parse_run("run", "a", "x", "y")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo"])

    def test_evaluate_arg(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "operations": {"b": ["echo {{args.0}}"]},
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e, \
                self.mock_subprocess_runner() as p:
            a.parse_run("run", "b", "x", "y")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "x"])

    def test_expression_call_expression(self):
        a = DyngleApp()
        a.config = ConfigHandler.setup(
            {
                "dyngle": {
                    "expressions": {
                        "hello": "'Hello '+get('full-name')+'!'",
                        "full-name": "'Ms. ' + name",
                    },
                    "operations": {"say": ["echo '{{hello}}'"]},
                }
            }
        )
        with self.patchout() as o, self.patcherr() as e, \
            self.mock_subprocess_runner() as p, self.patch_stream(
            "name: A"
        ):
            a.parse_run("run", "say")
        c = p.call_args.args[0]
        self.assertEqual(c, ["echo", "Hello Ms. A!"])
