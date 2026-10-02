from typing import Callable
import datetime
from pathlib import PurePath
import math
import json
import re
import yaml
import os
from urllib import parse

from dyngle.error import DyngleError
from dyngle.model.context import Context
from dyngle.model.template import Template
from dyngle.model.util import yamlify


def dtformat(dt: datetime, format_string=None) -> str:
    """Safe datetime formatting using Python's str.format() with named components.

    Available components: year, month, day, hour, minute, second, microsecond, weekday.
    Example: dtformat(datetime.now(), '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}')
    """
    if format_string is None:
        format_string = "{year:04d}{month:02d}{day:02d}"
    components = {
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "minute": dt.minute,
        "second": dt.second,
        "microsecond": dt.microsecond,
        "weekday": dt.weekday(),  # Monday is 0
    }
    return format_string.format(**components)


GLOBALS = {
    "__builtins__": {
        # Basic data types and conversions
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,
        # Essential functions
        "len": len,
        "min": min,
        "max": max,
        "next": next,
        "sum": sum,
        "abs": abs,
        "round": round,
        "sorted": sorted,
        "reversed": reversed,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
        "type": type,
    },
    # Read-only perations selected for inclusion
    "math": math,
    "datetime": datetime.datetime,
    "timedelta": datetime.timedelta,
    "dtformat": dtformat,
    "re": re,
    "PurePath": PurePath,
    "getenv": os.getenv,
    "getcwd": os.getcwd,
    "gethome": lambda: os.path.expanduser("~"),
    "to_json": lambda v: json.dumps(v, default=str),
    "from_json": json.loads,
    "to_yaml": lambda v: yamlify(v),
    "from_yaml": yaml.safe_load,
    "parse": parse,
}


def _evaluate(expression: str, locals: dict) -> str:
    """Evaluate a Python expression with safe globals and user data context.

    Safely evaluates a Python expression string using a restricted set of
    global functions and modules, combined with user-provided data. The
    expression is evaluated in a sandboxed environment that includes basic
    Python built-ins, mathematical operations, date/time handling, and data
    manipulation utilities.

    Parameters
    ----------
    expression : str
        A valid Python expression string to be evaluated.
    data : dict
        Dictionary containing variables and values to be made available during
        expression evaluation. Note that hyphens in keys will be replaced by
        underscores to create valid Python names.

    Returns
    -------
    str
        String representation of the evaluated expression result. If the result
        is a tuple, returns the string representation of the last element.

    Raises
    ------
    DyngleError
        If the expression contains invalid variable names that are not found in
        the provided data dictionary or global context.
    """
    try:
        result = eval(expression, {**GLOBALS, **locals})
    except KeyError as error:
        raise DyngleError(
            f"The following expression contains "
            + f"invalid name '{error}:\n{expression}"
        )

    # Allow the use of a comma to separate sub-expressions, which can then use
    # warus to set values, and only the last expression in the list returns a
    # value.
    result = result[-1] if isinstance(result, tuple) else result

    return result


class Expression:
    """A callable dyngle expression, distinguishable from generic callables."""

    def __init__(self, func: Callable):
        self._func = func

    def __call__(self, context=None):
        return self._func(context)

    def bind(self, context):
        """Return a callable that uses context by default, but accepts an explicit override."""
        def bound(*args):
            return self(args[0] if args else context)
        return bound


# The 'expression' function returns the expression object itself, which is
# really just a function.


def expression(text: str) -> Expression:
    """Generate an expression, which is a function based on a string
    expression"""

    def definition(context: Context | dict | None = None) -> str:
        """The expression function itself"""


        # We only work if passed some data to use - also we don't know our name
        # so can't report it.

        if context is None:
            raise DyngleError("Expression called with no argument")


        # We're converting it to Context in
        # case for some reason we were passed a raw dict.

        context = Context(context)


        # Translate names to underscore-separated instead of hyphen-separated
        # so they work within the Python namespace.

        symbols = Context()
        for key, val in context.items():
            symkey = key.replace("-", "_")
            symval = val.bind(context) if isinstance(val, Expression) else val
            symbols[symkey] = symval


        # Legacy functions: Create a get function which allows references using
        # the hyphen syntax too - note it relies on the original context object
        # (not the locals with the key replacement).

        def get(key):
            return context.resolve(key)

        def format(template_string):
            """Function in expressions to perform Dyngle template rendering"""
            return Template(template_string).render(context)

        # Passing the context in again allows function(data) in expressions
        symbols = symbols | {"get": get, "format": format, "data": context}


        # Perform the Python eval, expanded above
        return _evaluate(text, symbols)

    return Expression(definition)


def expression_structure(structure: dict | list) -> Callable[[dict], any]:
    """Generate an expression from a YAML structure (dict/list).

    Converts a YAML structure into an expression function that recursively
    evaluates string values as Python expressions while preserving the
    structure.
    """

    def definition(context: Context | dict | None = None):
        """The expression function that evaluates the YAML structure"""
        if context is None:
            raise DyngleError("Expression called with no argument")

        # Convert to Context to ensure consistent behavior
        context = Context(context)

        def evaluate_structure(obj):
            """Recursively evaluate a structure"""
            if isinstance(obj, dict):
                return {k: evaluate_structure(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [evaluate_structure(item) for item in obj]
            elif isinstance(obj, str):
                # Create an expression for this string and evaluate it
                expr = expression(obj)
                return expr(context)
            else:  # pragma: nocover
                # Other types (numbers, booleans, None) pass through
                return obj

        return evaluate_structure(structure)

    return Expression(definition)


def template_structure(
    structure: dict | list | str | int | float | bool,
) -> Callable[[dict], any]:
    """Generate an expression from a template structure.

    Similar to expression_structure, but wraps string values in format()
    calls automatically. Non-string primitives (int, float, bool) are
    treated as constants and returned as-is.
    """

    def definition(context: Context | dict | None = None):
        """The expression function that evaluates the template structure"""
        if context is None:
            raise DyngleError("Expression called with no argument")

        # Convert to Context to ensure consistent behavior
        context = Context(context)

        def evaluate_structure(obj):
            """Recursively evaluate a structure"""
            if isinstance(obj, dict):
                return {k: evaluate_structure(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [evaluate_structure(item) for item in obj]
            elif isinstance(obj, str):
                # Wrap string in format() and evaluate
                # Use repr() to properly escape the string for Python eval
                expr = expression(f"format({repr(obj)})")
                return expr(context)
            else:
                # Other types (numbers, booleans, None) pass through as
                # constants
                return obj

        return evaluate_structure(structure)

    return Expression(definition)
