from unittest.mock import Mock, patch

from dyngle import DyngleApp
from dyngle.command.run_command import RunCommand
from dyngle.model.template import Template
from test import DyngleTestCase


class TestTemplateRendering(DyngleTestCase):

    def test_data_no_dot(self):
        t = Template("a {{b}}")
        d = {"b": "x"}
        r = t.render(d)
        self.assertEqual("a x", r)

    def test_hyphen_in_name(self):
        t = Template("a {{b-c}}")
        d = {"b-c": "x"}
        r = t.render(d)
        self.assertEqual("a x", r)

    def test_nested_value(self):
        t = Template("a {{b.c}}")
        d = {"b": {"c": "x"}}
        r = t.render(d)
        self.assertEqual("a x", r)

    def test_multiple_entries(self):
        t = Template("a {{b}} {{c}}")
        d = {"b": "x", "c": "y"}
        r = t.render(d)
        self.assertEqual("a x y", r)

    def test_with_expression(self):
        t = Template("a {{b}}")
        e = {"b": lambda n: "x"}
        r = t.render(e)
        self.assertEqual(r, "a x")

    def test_with_expression_with_hyphen(self):
        t = Template("a {{b-c}}")
        e = {"b-c": lambda n: "x"}
        r = t.render(e)
        self.assertEqual(r, "a x")
