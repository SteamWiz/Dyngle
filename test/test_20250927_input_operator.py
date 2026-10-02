from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestInputOperator(DyngleTestCase):

    def test_input_operator(self):
        y = {
            "dyngle": {
                "expressions": {"b": '"x"'},
                "operations": {"a": ["b -> cat => output"]},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e, self.patch_stream(""):
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        # stdout is captured to output variable, not printed
        self.assertEqual(t.captured, "")

    def test_dotted_path(self):
        d = {"a": {"b": "x"}}
        c = {"dyngle": {"operations": {"c": ["a.b -> cat => output"]}}}
        with NamedTemporaryFile(mode="w+") as df, NamedTemporaryFile(
            mode="w+"
        ) as cf:
            safe_dump(c, cf)
            safe_dump(d, df)
            cf.seek(0)
            df.seek(0)
            with self.subprocess_runner_trap() as t, self.patchout() as o, \
                    self.patcherr() as e:
                DyngleApp.start(
                    "--config",
                    cf.name,
                    "--stream",
                    df.name,
                    "run",
                    "c",
                    debug=True,
                )
        # stdout is captured to output variable, not printed
        self.assertEqual(t.captured, "")
