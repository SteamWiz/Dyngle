from datetime import datetime
from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from dyngle.model.expression import expression
from test import DyngleTestCase


class TestRawDataTemplate(DyngleTestCase):

    def test_expressions_reference_int(self):
        y = {
            "dyngle": {
                "expressions": {"i": "24", "t": 'type(get("i")).__name__'},
                "operations": {"a": {"steps": ["{{t}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["int"])

    def _test_type(self, expression, typename):
        y = {
            "dyngle": {
                "expressions": {
                    "x": expression,
                    "t": 'type(get("x")).__name__',
                },
                "operations": {"a": {"steps": ["{{t}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, [typename])

    def test_datetime(self):
        self._test_type("datetime(2024,1,1,5,23,45)", "datetime")

    def test_list(self):
        self._test_type('["a"]', "list")

    def test_dict(self):
        self._test_type('{"a":"b"}', "dict")

    def test_set(self):
        self._test_type('{"a"}', "set")

    # Tuples are handled differently - they can be used within expressions but
    # when resolved out of the expression, we only keep the last value.

    def test_tuple_expr(self):
        e = expression("None,(3,4)")
        r = e({})
        self.assertEqual((3, 4), r)

    def test_bool(self):
        self._test_type("(a:=5), a==5", "bool")

    # Data types converted to strings locgically when inserted into commands

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
        self._test_resolved("1+2", "3")

    # def test_resolved_bool(self):
    #     self._test_resolved("3==3", ".")

    def test_resolved_datetime(self):
        self._test_resolved("datetime(2024,3,4,5,6,7)", "2024-03-04 05:06:07")

    # def test_resolved_list(self):
    #     self._test_resolved("[3,4]", 3)

    def test_resolved_set(self):
        self._test_resolved("set([4])", '{4}')

    # def test_resolved_error(self):
    #     with self.assertRaises(DyngleError):
    #         self._test_resolved('re.compile(".*")', "")

    # `values:` That contains any YAML/Python-compliant data types

    def _test_global_values(self, value, outcome):
        y = {
            "dyngle": {
                "constants": {"x": value},
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

    def test_global_value_str(self):
        self._test_global_values("abc", "abc")

    def test_global_value_dict(self):
        self._test_global_values("a: b", "a: b")

    def test_global_value_expression(self):
        y = {
            "dyngle": {
                "constants": {"x": [3, 5]},
                "operations": {
                    "a": {"expressions": {"s": "sum(x)"}, "steps": ["{{s}}"]}
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["8"])

    def _test_local_values(self, value, outcome):
        y = {
            "dyngle": {
                "operations": {
                    "a": {"constants": {"x": value}, "steps": ["{{x}}"]}
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, [outcome])

    def test_local_value_str(self):
        self._test_local_values("abc", "abc")

    def test_local_value_dict(self):
        self._test_local_values("a: b", "a: b")

    def test_resolved_path(self):
        self._test_resolved("PurePath('f')", "f")
