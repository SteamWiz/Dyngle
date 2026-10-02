from functools import cached_property

from dyngle.model.expression import (
    expression, expression_structure, template_structure
)
from dyngle.model.context import Context
from dyngle.model.operation import Operation


RUNTIME_DECLARATIONS = { 'runtime': {
    'args': expression("get('args') if 'args' in data else []")
}}

class Toolset:
    """Represents the entire set of definitions for operations, expressions,
    and constants.

    The Dyngleverse acts as a registry/index for all operations and global
    constants (constants and expressions). It maintains:

    - operations: A dict of Operation objects indexed by name
    - global_constants: A Context containing global constants and expressions

    When operations are created, they receive a reference to global_constants
    and merge them with their own local constants, establishing the proper
    scoping hierarchy:

    1. Global constants (lowest precedence)
    2. Local operation constants (higher precedence)
    3. Live data from execution (highest precedence, shared across operations)
    """

    def __init__(self, app=None):
        self.app = app
        self.operations = {}
        self.global_declarations = Context()

    def load_declarations(self, config: dict):
        """
        Load only the constants and expressions from a config.
        This allows for two-phase loading where all constants are loaded first,
        then all operations are created with access to all declarations.
        """
        self.global_declarations |= Toolset.parse_declarations(config)

    def load_operations(self, config: dict):
        """
        Load only the operations from a config.
        Should be called after all constants have been loaded.
        """
        ops_defs = config.get("operations") or {}
        for key, op_def in ops_defs.items():
            operation = Operation(self, op_def, key)
            self.operations[key] = operation

    @staticmethod
    def parse_declarations(definition: dict) -> Context:
        """
        At either the global (toolset) or local (within an operation)
        level, we might find constants, expressions, and templates.
        
        Expressions can be either:
        - Strings (traditional Python expression syntax)
        - Dicts/lists (YAML structure syntax)
        
        Templates automatically wrap strings in format() calls:
        - Strings become format('string')
        - Dicts/lists are processed recursively
        - Non-string primitives (int, float, bool) are treated as constants
        """

        expr_defs = definition.get("expressions") or {}
        expressions = {}
        for k, v in expr_defs.items():
            if isinstance(v, str):
                # Traditional string expression
                expressions[k] = expression(v)
            elif isinstance(v, (dict, list)):
                # YAML structure expression
                expressions[k] = expression_structure(v)
            else:
                # Other types (shouldn't happen, but handle gracefully)
                expressions[k] = expression(str(v))

        template_defs = definition.get("templates") or {}
        templates = {}
        for k, v in template_defs.items():
            # All template values use template_structure
            templates[k] = template_structure(v)

        constants = definition.get("constants") or {}

        return (Context(expressions) | templates | constants
                | RUNTIME_DECLARATIONS)

