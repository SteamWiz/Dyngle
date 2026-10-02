from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestFixBugStringifySafepath(DyngleTestCase):

    def _test_resolved(self, expr, outcome):
        y = {
            "dyngle": {
                "expressions": {"x": expr},
                "operations": {"a": {"steps": ["{{x}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, [outcome])

    def test_resolved_int(self):
        self._test_resolved('PurePath("foo")', "foo")
