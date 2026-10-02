from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from test import DyngleTestCase


class TestNestedObjectProperty(DyngleTestCase):

    def test_nested_dict_from_expression(self):
        """Test accessing nested properties of dict returned by expression"""
        y = {
            "dyngle": {
                "expressions": {"d": "{'a': {'b': 'c'}}"},
                "operations": {"op": {"steps": ["{{d.a.b}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["c"])

    def test_nested_dict_from_json_loads(self):
        """Test accessing nested properties after json.loads()"""
        y = {
            "dyngle": {
                "constants": {"j": '{"x": {"y": 42}}'},
                "expressions": {"d": "from_json(get('j'))"},
                "operations": {"op": {"steps": ["{{d.x.y}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["42"])

    def test_nested_dict_from_yaml_loads(self):
        """Test accessing nested properties after yaml.safe_load()"""
        y = {
            "dyngle": {
                "constants": {"s": "k:\n  v: 7"},
                "expressions": {"d": "from_yaml(s)"},
                "operations": {"op": {"steps": ["{{d.k.v}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["7"])

    def test_deeply_nested_access(self):
        """Test accessing deeply nested properties"""
        y = {
            "dyngle": {
                "expressions": {"d": "{'a': {'b': {'c': {'d': 'deep'}}}}"},
                "operations": {"op": {"steps": ["{{d.a.b.c.d}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "op", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["deep"])
