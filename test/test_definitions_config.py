from tempfile import NamedTemporaryFile

from yaml import safe_dump

from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestDefinitionsConfig(DyngleTestCase):

    def test_operations_in_config(self):
        y = {"dyngle": {"operations": {"a": ["b"]}}}
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
            c = p.call_args.args[0]
            self.assertEqual(c, ["b"])

    def test_expression_in_config(self):
        y = {
            "dyngle": {
                "operations": {"a": ["{{b}}"]},
                "expressions": {"b": "'x'"},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
            c = p.call_args.args[0]
            self.assertEqual(c, ["x"])

    def test_no_operations_in_config(self):
        y = {"dyngle": {}}
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                with self.assertRaises(DyngleError) as e:
                    DyngleApp.start("--config", f.name, "run", "a", debug=True)
            r = str(e.exception)
            self.assertIn("Invalid operation", r)

    def test_external_operations(self):
        y1 = {"dyngle": {"operations": {"a": ["b"]}}}
        with NamedTemporaryFile(mode="w+") as f1:
            safe_dump(y1, f1)
            f1.seek(0)
            y2 = {"dyngle": {"imports": [f1.name]}}
            with NamedTemporaryFile(mode="w+") as f2:
                safe_dump(y2, f2)
                f2.seek(0)
                with self.patchout() as o, self.patcherr() as e, \
                        self.mock_subprocess_runner() as p:
                    DyngleApp.start(
                        "--config", f2.name, "run", "a", debug=True
                    )
            c = p.call_args.args[0]
            self.assertEqual(c, ["b"])

    def test_external_precedence_mine(self):
        y1 = {"dyngle": {"operations": {"a": ["b"]}}}
        with NamedTemporaryFile(mode="w+") as f1:
            safe_dump(y1, f1)
            f1.seek(0)
            y2 = {"dyngle": {"operations": {"a": ["c"]}, "imports": [f1.name]}}
            with NamedTemporaryFile(mode="w+") as f2:
                safe_dump(y2, f2)
                f2.seek(0)
                with self.patchout() as o, self.patcherr() as e, \
                        self.mock_subprocess_runner() as p:
                    DyngleApp.start(
                        "--config", f2.name, "run", "a", debug=True
                    )
            c = p.call_args.args[0]
            self.assertEqual(c, ["c"])

    def test_external_precedence_last(self):
        y1 = {"dyngle": {"operations": {"a": ["b"]}}}
        with NamedTemporaryFile(mode="w+") as f1:
            safe_dump(y1, f1)
            f1.seek(0)
            y2 = {"dyngle": {"operations": {"a": ["y"]}}}
            with NamedTemporaryFile(mode="w+") as f2:
                safe_dump(y2, f2)
                f1.seek(0)
                y2 = {"dyngle": {"imports": [f1.name, f2.name]}}
                with NamedTemporaryFile(mode="w+") as f2:
                    safe_dump(y2, f2)
                    f2.seek(0)
                    with self.patchout() as o, self.patcherr() as e, \
                            self.mock_subprocess_runner() as p:
                        DyngleApp.start(
                            "--config", f2.name, "run", "a", debug=True
                        )
            c = p.call_args.args[0]
            self.assertEqual(c, ["y"])

    def test_expression_import(self):
        y1 = {"dyngle": {"expressions": {"b": "'x'"}}}
        with NamedTemporaryFile(mode="w+") as f1:
            safe_dump(y1, f1)
            f1.seek(0)
            y2 = {
                "dyngle": {
                    "operations": {"a": ["{{b}}"]},
                    "imports": [f1.name],
                }
            }
            with NamedTemporaryFile(mode="w+") as f2:
                safe_dump(y2, f2)
                f2.seek(0)
                with self.patchout() as o, self.patcherr() as e, \
                        self.mock_subprocess_runner() as p:
                    DyngleApp.start(
                        "--config", f2.name, "run", "a", debug=True
                    )
            c = p.call_args.args[0]
            self.assertEqual(c, ["x"])
