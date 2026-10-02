from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestNestedImports(DyngleTestCase):

    def test_import_1_level(self):
        y1 = {"dyngle": {"operations": {"a": ["b"]}}}
        with NamedTemporaryFile(mode="w+") as f1:
            safe_dump(y1, f1)
            f1.seek(0)
            y2 = {"dyngle": {"imports": [f1.name]}}
            with NamedTemporaryFile(mode="w+") as f2:
                safe_dump(y2, f2)
                f2.seek(0)
                with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                    DyngleApp.start(
                        "--config", f2.name, "run", "a", debug=True
                    )
            c = p.call_args.args[0]
            self.assertEqual(c, ["b"])

    def test_import_2_levels(self):
        with NamedTemporaryFile(mode="w+") as f1:
            y1 = {"dyngle": {"operations": {"a": ["b"]}}}
            safe_dump(y1, f1)
            f1.seek(0)
            with NamedTemporaryFile(mode="w+") as f2:
                y2 = {"dyngle": {"imports": [f1.name]}}
                safe_dump(y2, f2)
                f2.seek(0)
                with NamedTemporaryFile(mode="w+") as f3:
                    y3 = {"dyngle": {"imports": [f2.name]}}
                    safe_dump(y3, f3)
                    f3.seek(0)
                    with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                        DyngleApp.start(
                            "--config", f3.name, "run", "a", debug=True
                        )
            c = p.call_args.args[0]
            self.assertEqual(c, ["b"])

    def test_no_loops(self):
        with NamedTemporaryFile(mode="w+") as f1, NamedTemporaryFile(
            mode="w+"
        ) as f2:
            y1 = {
                "dyngle": {"operations": {"a": ["b1"]}, "imports": [f2.name]}
            }
            y2 = {
                "dyngle": {"operations": {"a": ["b2"]}, "imports": [f1.name]}
            }
            safe_dump(y1, f1)
            f1.seek(0)
            safe_dump(y2, f2)
            f2.seek(0)

            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f1.name, "run", "a", debug=True)
            c = p.call_args.args[0]
            self.assertEqual(c, ["b1"])
