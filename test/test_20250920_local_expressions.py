from tempfile import NamedTemporaryFile

from yaml import safe_dump
from dyngle import DyngleApp
from dyngle.error import DyngleError
from test import DyngleTestCase


class TestLocalExpressions(DyngleTestCase):

    def test_invalid_data_key_error(self):
        y = {
            "dyngle": {
                "operations": {"a": {"steps": ["{{b}}"]}},
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                with self.assertRaises(DyngleError):
                    DyngleApp.start("--config", f.name, "run", "a", debug=True)

    # def test_invalid_op_config_error(self):
    #     y = {'dyngle': {
    #         'operations': {
    #             'a': 'x'
    #         },
    #     }}
    #     with NamedTemporaryFile(mode='w+') as f:
    #         safe_dump(y, f)
    #         f.seek(0)
    #         with \
    #                 self.patchout() as o, self.patcherr() as e, \
    #                 self.mock_subprocess_runner() as p:
    #             with self.assertRaises(DyngleError):
    #                 DyngleApp.start('--config', f.name,
    #                                 'run', 'a', debug=True)

    def test_local_expressions(self):
        y = {
            "dyngle": {
                "operations": {
                    "a": {"expressions": {"b": "'x'"}, "steps": ["{{b}}"]}
                },
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

    def test_local_expressions_with_logic(self):
        y = {
            "dyngle": {
                "operations": {
                    "a": {
                        "expressions": {"b": "len([2,3])"},
                        "steps": ["{{b}}"],
                    }
                },
            }
        }
        with NamedTemporaryFile(mode="w+") as f:
            safe_dump(y, f)
            f.seek(0)
            with self.patchout() as o, self.patcherr() as e, \
                    self.mock_subprocess_runner() as p:
                DyngleApp.start("--config", f.name, "run", "a", debug=True)
        c = p.call_args.args[0]
        self.assertEqual(c, ["2"])
