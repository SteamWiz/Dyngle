from dyngle import DyngleApp
from test import DyngleTestCase

CONFIG_WITH_MULTI = """
dyngle:
  operations:
    test:
      constants:
        input: '{"a":"b"}'
        multi:
          - '-r'
          - '.a'
      steps:
        - input -> echo jq {{multi}} => result
      returns: result
""".lstrip()

CONFIG_WITH_SINGLE = """
dyngle:
  operations:
    test:
      constants:
        input: '{"a":"b"}'
        single: '.a'
      steps:
        - input -> echo jq -r {{single}} => result
      returns: result
""".lstrip()

CONFIG_WITH_JSON = """
dyngle:
  operations:
    test:
      constants:
        topics:
          - alpha
          - beta
      steps:
        - echo "I like {{topics}}" => result
      returns: result
""".lstrip()

CONFIG_WITH_STRING = """
dyngle:
  operations:
    test:
      constants:
        love: Baseball
      steps:
        - echo "I like {{love}}" => result
      returns: result
""".lstrip()

MULTI_STRING = """
dyngle:
  operations:
    test:
      constants:
        good: Paul
        better: Amor
      steps:
        - echo "I like {{good}} but mostly {{better}}" => result
      returns: result
""".lstrip()

DICT = """
dyngle:
  operations:
    test:
      constants:
        options:
            a: b
            c: d
      steps:
        - echo {{options}} => result
      returns: result
"""

WITH_PATH = """
dyngle:
  operations:
    test:
      expressions:
        dirpath: PurePath('/etc/nothing')
      returns: dirpath
"""

WITH_INVALID_INDEX = """
dyngle:
  operations:
    test:
      constants:
        topics:
          - alpha
          - beta
      steps:
        - echo {{topics.1}} {{topics.2}} => result
      returns: result
""".lstrip()

FORMAT_EXPRESSION = """
dyngle:
  operations:
    test:
      expressions:
        path: PurePath('alpha')
        mydate: datetime(2025,1,2).date()
        full: format('{{path}}/beta on {{mydate}}')
      returns: full
""".lstrip()

YAML_PATH = """
dyngle:
  operations:
    test:
      expressions:
        path-yaml: to_yaml(PurePath('alpha'))
      returns: path-yaml
""".lstrip()


class TestMultiKey(DyngleTestCase):

    def test_multi_key(self):
        with self.configured_app(CONFIG_WITH_MULTI) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('jq -r .a', o.read())

    def test_single_key(self):
        with self.configured_app(CONFIG_WITH_SINGLE) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('jq -r .a', o.read())

    def test_json_string(self):
        with self.configured_app(CONFIG_WITH_JSON) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('I like ["alpha", "beta"]', o.read())

    def test_plain_string(self):
        with self.configured_app(CONFIG_WITH_STRING) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('I like Baseball', o.read())

    def test_plain_string(self):
        with self.configured_app(MULTI_STRING) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('I like Paul but mostly Amor', o.read())

    def test_dict_options(self):
        with self.configured_app(DICT) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('--a b --c d', o.read())

    def test_with_path(self):
        with self.configured_app(WITH_PATH) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('/etc/nothing', o.read())

    def test_with_path(self):
        with self.configured_app(WITH_INVALID_INDEX) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('beta', o.read())

    def test_format_expression(self):
        with self.configured_app(FORMAT_EXPRESSION) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('alpha/beta on 2025-01-02', o.read())

    def test_path_yaml(self):
        with self.configured_app(YAML_PATH) as (a, o, e):
            a.parse_run('run','test')
        self.assertEqual('alpha\n', o.read())
