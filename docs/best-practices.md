# Best Practices

Guidelines for writing effective Dyngle operations. These practices help create operations that are reliable, maintainable, and work correctly across different execution contexts.

## Operation Design

**Use hyphen-separated keys:** Always use hyphen-separated strings (like `my-variable`) for YAML keys in expressions, constants, and operation names. Never use underscore-separated strings (like `my_variable`). This maintains consistency across your configuration.

**Return structured results:** Operations should return results as dicts with named fields. Add nested dicts and lists as appropriate to represent the data structure clearly.

**Parse string outputs:** If a command step produces a string containing structured data, parse it in expressions to return a structured result rather than a raw string.

**Accept inputs via schema:** Define operation inputs using the [`accepts:`](inputs-and-interfaces.md) attribute to validate and default input data.

**Document field purposes:** Add `description:` to each field in your `accepts:` schema. Field descriptions are passed through to MCP tools and help users understand parameters in dynamic contexts like APIs or MCP servers.

**Output troubleshooting info:** Operations may optionally write useful troubleshooting information to stdout during execution.

## Expression Usage

**Use expressions for logic:** Use Dyngle [expressions](constants-and-expressions.md) for logic and string or data manipulation. Avoid `bash -c` and `python -c` command steps.

**Break up long expressions:** Avoid long multi-line expressions. Break them into multiple expressions that reference each other using `get()`, without losing logic or functionality.

**Handle missing values:** The `get()` function returns a blank string if the value isn't found. Use the `or` operator to specify defaults: `get('value') or 'default'`.

**Reference expressions with get()**: When one expression references another expression's value, always use `get('expression-name')`. Direct variable references only work for input values and context data, not for other expressions.

**Use YAML objects over Python dicts:** When defining structured data in expressions, use YAML object syntax instead of Python dict strings. YAML objects are easier to read, parse, and maintain. For example, instead of `result: "{'path': get('abs-path'), 'items': get('items')}"`, use:

```yaml
result:
  path: get('abs-path')
  items: get('items')
```

## Command Steps

**Store multiline scripts as constants:** In rare cases where the logic required for an operation can't be achieved using system commands in command steps, conditionals in conditional steps, and/or Pythonic expressions in `expressions:`, you may need a full inline script. When you do, store the script body as a YAML literal block scalar (`|`) under `constants:` and reference it in the step with `{{script-name}}`. Pass dynamic values as positional arguments (`sys.argv`) rather than embedding template placeholders inside the script body — this keeps the script pure and readable.

```yaml
constants:
  parse-changelog: |
    import sys, re
    content = open(sys.argv[1]).read()
    entries = re.findall(r'## \[(.+?)\]\n(.*?)(?=\n## |\Z)', content, re.S)
    for ver, body in entries:
        for line in body.strip().splitlines():
            print(f'{ver}: {line.strip()}')
steps:
  - python3 -c {{parse-changelog}} {{changelog-path}} => parsed-entries
```

**Produce directly testable outputs:** Avoid writing a separate expression just to evaluate a value in an `if:` condition. Instead, make the upstream expression or command output something directly testable. For expressions, any truthy Python value works as-is. For command step output, use pseudo-boolean strings: empty string (`''`) for false, any non-empty string (e.g. `'x'`) for true — capture it with `=>` and reference the variable directly in `if:`.

```yaml
steps:
  - python3 -c {{check-script}} {{arg}} => condition-met
  - if: condition-met
    then:
      - ...
```

## Control Flow

**Use named expressions for conditions:** Always define conditions as named expressions rather than inline. This makes operations more readable and testable. For example:

```yaml
expressions:
  is-production: "environment == 'production'"
steps:
  - if: is-production
    then:
      - echo "Production deployment"
```

**Prefer conditionals over complex expressions:** When logic becomes complex, use [conditional steps](command-steps.md#conditional-steps) with `if/then/else` rather than trying to handle all cases in expressions.

**Keep conditional blocks focused:** Each conditional block should handle a single logical decision. Use nested conditionals for multiple decision points rather than combining logic into complex expressions.

## Path Management

**Prefer absolute paths:** Operations may run in daemons, cron jobs, or other non-interactive contexts. Prefer absolute paths over relative paths for file operations.

**Convert relative to absolute:** Many command steps interpret path arguments relative to the current working directory. Operations should contain logic to convert relative paths to absolute paths.

**Use path functions:** Use `getcwd()` and `PurePath()` for path manipulation in expressions.

**Handle environment variables carefully:** Environment variables like `HOME` can be accessed via `getenv()` when needed, but operations should not assume they exist in all execution contexts.

## Example

This example demonstrates several best practices: accepting inputs with defaults, converting relative paths to absolute, parsing command output into structured data, and returning a well-structured result.

```yaml
    list-directory:
      description: List contents of a directory with name, type, and size for each item (includes hidden files)
      accepts:
        path:
          type: string
          default: "."
          description: Directory path to list (relative or absolute)
      expressions:
        # Convert relative path to absolute path
        is-absolute: "get('path').startswith('/')"
        relative-to-abs: "str(PurePath(getcwd()) / get('path'))"
        abs-path: "get('path') if get('is-absolute') else get('relative-to-abs')"
        # Parse ls output into structured data
        # Each line format: "permissions links owner group size month day time name"
        lines: "get('raw-listing').strip().split('\\n')"
        filtered-lines: "[line for line in get('lines') if line.strip() and not line.startswith('total')]"
        # Extract names from each line (last field)
        names: "[line.split()[-1] for line in get('filtered-lines')]"
        # Determine types (directory or file based on first character)
        types: "['directory' if line.startswith('d') else 'file' for line in get('filtered-lines')]"
        # Extract sizes (5th field, 0-indexed position 4)
        sizes: "[int(line.split()[4]) if line.split()[4].isdigit() else 0 for line in get('filtered-lines')]"
        # Combine into list of dicts
        items: "[{'name': n, 'type': t, 'size': s} for n, t, s in zip(get('names'), get('types'), get('sizes'))]"
        result:
          path: get('abs-path')
          items: get('items')
      steps:
        # Use ls -la to get detailed listing including hidden files
        # -l: long format with details
        # -a: include hidden files (starting with .)
        - ls -la {{abs-path}} => raw-listing
      returns: result
```

Note how the example:
- Uses `accepts:` with a default value for the path input
- Converts relative paths to absolute using expressions
- Uses hyphen-separated keys consistently throughout
- Breaks complex parsing into multiple small expressions
- Returns a structured dict with named fields using YAML object syntax instead of Python dict strings
