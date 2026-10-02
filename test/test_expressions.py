from dyngle.error import DyngleError
from dyngle.model.expression import expression
from test import DyngleTestCase


class Testexpressions(DyngleTestCase):

    def test_evaluation(self):
        e = expression("'a'+'b'")
        r = e({})
        self.assertEqual("ab", r)

    def test_numeric(self):
        e = expression("1+4")
        r = e({})
        self.assertIsInstance(r, int)

    def test_static_input(self):
        e = expression("'a'+'b'")
        r = e({})
        self.assertEqual("ab", r)

    def test_read_data(self):
        e = expression("'Hello ' + name + '!'")
        r = e({"name": "lightning"})
        self.assertEqual(r, "Hello lightning!")

    def test_builtin(self):
        e = expression("len('abcd')")
        r = e({})
        self.assertEqual(4, r)

    def test_no_locals(self):
        e = expression("self")
        with self.assertRaises(NameError):
            r = e({})

    def test_invalid_method(self):
        e = expression("datetime.now().strftime('%Y%m%d')")
        with self.assertRaises(DyngleError):
            r = e({})

    def test_alternate_date_formatting(self):
        e = expression("dtformat(datetime(2020,9,6))")
        r = e({})
        self.assertEqual("20200906", r)

    # def test_safe_path_operations(self):
    #     e = expression("Path('.').is_dir()")
    #     r = e({})
    #     self.assertEqual(True, r)

    # def test_path_default(self):
    #     e = expression("Path().is_dir()")
    #     r = e({})
    #     self.assertEqual(True, r)

    # def test_multiple_operations(self):
    #     e = expression(
    #         "(p:=Path()/'delete-me.x').write_text('a'),p.read_text()"
    #     )
    #     r = e({})
    #     self.assertEqual("a", r)

    def test_data_key_hyphen(self):
        e = expression("'Hello ' + my_name + '!'")
        r = e({"my-name": "lightning"})
        self.assertEqual(r, "Hello lightning!")

    def test_expression_calls_expression_1x(self):
        e = expression("get('b')")
        d = {"b": expression('"z"')}
        r = e(d)
        self.assertEqual(r, "z")

    def test_expression_calls_expression_2x(self):
        e = expression('get("a")')
        d = {"a": expression('get("b")'), "b": "z"}
        r = e(d)
        self.assertEqual(r, "z")

    def test_with_newline(self):
        e = expression("'a'+'b'+'\\n'")
        r = e({})
        self.assertEqual("ab\n", r)

    def test_fail_if_called_with_none(self):
        e = expression('"y"')
        with self.assertRaises(DyngleError):
            e(None)

    def test_expression_calls_expression_as_name(self):
        e = expression("a({})")
        d = {"a": expression('"y"')}
        r = e(d)
        self.assertEqual(r, "y")

    def test_expression_calls_expression_no_args(self):
        e = expression("a()")
        d = {"a": expression('"y"')}
        r = e(d)
        self.assertEqual(r, "y")

    def test_expression_no_args_uses_current_context(self):
        e = expression("a()")
        d = {"a": expression("'Hello ' + name"), "name": "world"}
        r = e(d)
        self.assertEqual(r, "Hello world")
