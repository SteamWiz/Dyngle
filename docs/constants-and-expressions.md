# Constants, Expressions, and Templates

Constants, expressions, and templates allow you to define reusable values in your configuration. Constants are static values, expressions are dynamically evaluated using Python, and templates provide convenient string formatting.

## Constants

Define constants using the `constants:` key. Constants are static values that don't change during execution.

### Global Constants

Defined under `dyngle:` and available to all operations:

```yaml
dyngle:
  constants:
    environment: production
    region: us-west-2
    api-url: https://api.example.com
  operations:
    deploy:
      steps:
        - echo "Deploying to {{environment}} in {{region}}"
```

### Local Constants

Defined within a specific operation:

```yaml
dyngle:
  operations:
    greet:
      constants:
        greeting: Hello
        name: World
      steps:
        - echo "{{greeting}}, {{name}}!"
```

Local constants override global constants with the same name.

## Expressions

Expressions are Python code snippets that compute dynamic values. They're evaluated in real-time using the Python interpreter with a controlled set of available functions and variables specific to Dyngle.

### Basic Usage

Define expressions that evaluate to values:

```yaml
dyngle:
  operations:
    greet:
      expressions:
        greeting: "'Hello ' + name + '!'"
      steps:
        - echo "{{greeting}}"
```

Run it:

```bash
echo "name: Alice" | dyngle run greet
```

Output:

```text
Hello Alice!
```

### Expressions vs Constants

An expression is like a constant that is evaluated dynamically:

```yaml
dyngle:
  constants:
    static-time: "2024-01-01"  # Always the same
  expressions:
    current-time: "datetime.now()"  # Evaluated each time
```

### Global Expressions

Defined under `dyngle:` and available to all operations:

```yaml
dyngle:
  expressions:
    timestamp: "datetime.now()"
    author: "'Francis Potter'"
  operations:
    log:
      steps:
        - echo "[{{timestamp}}] Log by {{author}}"
```

### Local Expressions

Defined within a specific operation:

```yaml
dyngle:
  operations:
    say-hello:
      expressions:
        count: "len(name)"
      steps:
        - echo "Hello {{name}}! Your name has {{count}} characters."
```

Local expressions override global expressions with the same name.

## Templates

Templates provide a convenient way to define string templates without explicitly wrapping them in `format()` calls. They work like expressions but automatically apply template formatting to string values.

### Basic Usage

Define templates that automatically format strings:

```yaml
dyngle:
  constants:
    name: Alice
  templates:
    greeting: "Hello {{name}}!"
  operations:
    greet:
      steps:
        - echo "{{greeting}}"
```

This is equivalent to:

```yaml
dyngle:
  expressions:
    greeting: "format('Hello {{name}}!')"
```

### Templates vs Expressions

Templates are ideal when you primarily need string formatting:

```yaml
dyngle:
  constants:
    cmd: "ls"
    output: "result.txt"
  templates:
    # Automatically wrapped in format()
    full-command: "{{cmd}} --output {{output}}"
  expressions:
    # Requires explicit format() call
    full-command-expr: "format('{{cmd}} --output {{output}}')"
```

Both produce the same result, but templates are more concise for string formatting.

### Global Templates

Defined under `dyngle:` and available to all operations:

```yaml
dyngle:
  constants:
    app-name: MyApp
    version: 1.0
  templates:
    banner: "=== {{app-name}} v{{version}} ==="
  operations:
    start:
      steps:
        - echo "{{banner}}"
```

### Local Templates

Defined within a specific operation:

```yaml
dyngle:
  constants:
    user: admin
  operations:
    login:
      templates:
        message: "Logging in as {{user}}..."
      steps:
        - echo "{{message}}"
```

Local templates override global templates with the same name.

### Template Structures

Templates support complex data structures with automatic formatting:

**Dictionary structures:**

```yaml
dyngle:
  constants:
    host: example.com
    port: 8080
  templates:
    config:
      server: "{{host}}"
      url: "http://{{host}}:{{port}}"
  operations:
    show-config:
      expressions:
        server-info: "get('config')['server']"
      steps:
        - echo "{{server-info}}"
```

**List structures:**

```yaml
dyngle:
  constants:
    env: production
  templates:
    commands:
      - "echo Starting {{env}}"
      - "echo Deploying to {{env}}"
  operations:
    deploy:
      expressions:
        first-cmd: "get('commands')[0]"
      steps:
        - "{{first-cmd}}"
```

**Nested structures:**

```yaml
dyngle:
  constants:
    app: MyApp
    version: 2.0
  templates:
    metadata:
      info:
        name: "{{app}}"
        version: "{{version}}"
      tags:
        - "{{app}}-{{version}}"
        - "latest"
```

### Non-String Values

Non-string primitive values (integers, floats, booleans) in templates are treated as constants:

```yaml
dyngle:
  templates:
    config:
      name: "MyApp"      # String - formatted
      port: 8080         # Integer - constant
      enabled: true      # Boolean - constant
      timeout: 30.5      # Float - constant
```

This allows you to mix formatted strings with static values in the same structure.

## Template Syntax

Constants, expressions, and templates can be referenced in your configuration using template syntax. Dyngle supports two template syntaxes:

### Double-Curly Syntax

The traditional syntax uses double curly braces:

```yaml
dyngle:
  constants:
    name: Alice
    server:
      host: example.com
  operations:
    greet:
      steps:
        - echo "Hello {{name}}"
        - echo "Server: {{server.host}}"
```

This syntax works everywhere and supports inline replacements within strings.

### Dollar Syntax

An alternative syntax uses the dollar sign prefix:

```yaml
dyngle:
  constants:
    name: Alice
    server:
      host: example.com
  operations:
    greet:
      steps:
        - echo $name
        - echo $server.host
```

**Important constraints:**

- The `$variable` syntax only works when it's a complete word (after shell-style word splitting)
- It does **not** work for inline replacements: `echo "Hello$name"` will not be replaced
- It **does** work in quotes when it's a separate word: `echo "$name"` works
- It supports the same features as `{{...}}`: nested properties (`$server.host`), hyphens (`$first-name`), and numeric indices (`$runtime.args.0`)

**When to use dollar syntax:**

The dollar syntax is useful to avoid YAML parsing issues with curly braces in certain contexts. Both syntaxes can be used together in the same configuration:

```yaml
dyngle:
  constants:
    greeting: Hello
    name: World
  operations:
    greet:
      steps:
        - echo "$greeting, {{name}}!"  # Both work together
```

## Available Functions and Names

Expressions evaluate in a context that includes a subset of Python's standard features plus some Dyngle-specific functions. This controlled environment ensures expressions are powerful yet predictable.

### Referencing Context Values

Values from the operation context can be referenced directly as Python variables:

```yaml
dyngle:
  operations:
    greet:
      expressions:
        message: "'Hello ' + name"
      steps:
        - echo "{{message}}"
```

### Hyphenated Names

YAML keys can contain hyphens. To reference them in expressions:

**Option 1:** Replace hyphens with underscores:

```yaml
dyngle:
  operations:
    greet:
      expressions:
        message: "'Hello ' + first_name"  # References 'first-name'
      steps:
        - echo "{{message}}"
```

**Option 2:** Use the `get()` function:

```yaml
dyngle:
  operations:
    greet:
      expressions:
        message: "'Hello ' + get('first-name')"
      steps:
        - echo "{{message}}"
```

**Important:** The underscore form gives you the raw value for constants, but for **expressions** it gives you a callable. You must add `()` to invoke it and get the computed result. See [Calling Expressions from Expressions](#calling-expressions-from-expressions) for details.

## Calling Expressions from Expressions

When an expression name appears in the Python namespace of another expression, it is always a **callable** — not a plain value. This is true whether you reference it by its underscore-separated name or via `get()`. You must call it with `()` to obtain its computed value.

```yaml
dyngle:
  expressions:
    greeting: "'Hello ' + name"
    message: "greeting()"   # greeting is callable; greeting() gives the value
  operations:
    greet:
      steps:
        - echo "{{message}}"
```

Run with:

```bash
echo "name: Alice" | dyngle run greet
```

Output:

```text
Hello Alice!
```

Note that `get()` is different: it resolves the expression automatically and returns the computed value, so no `()` is needed when using `get()`:

```yaml
dyngle:
  expressions:
    first-name: "name.split()[0]"
    message-a: "first_name()"          # underscore form — must call with ()
    message-b: "get('first-name')"     # get() resolves the expression — no () needed
```

Contrast this with a **constant**, which is a plain value regardless of how you access it:

```yaml
dyngle:
  constants:
    greeting: Hello          # plain value
  expressions:
    first-name: "name.split()[0]"   # expression — callable in the namespace
    message: "greeting + ' ' + first_name()"  # greeting is a value; first_name() is called
```

An explicit context can still be passed if needed — `greeting(data)` — which is equivalent to the old call style and remains supported.

This also applies when the expression being called is a structure:

```yaml
dyngle:
  expressions:
    config:
      host: "format('{{server-host}}')"
      port: "int(get('server-port'))"
    host-value: "config()['host']"   # config is an expression, so config() to invoke it
```

## Dyngle-Specific Functions

### get()

Retrieve values from the operation context by name:

```yaml
dyngle:
  expressions:
    full-greeting: "'Hello ' + get('first-name') + ' ' + get('last-name')"
```

The `get()` function can also reference other expressions:

```yaml
dyngle:
  expressions:
    greeting: "'Hello'"
    full-greeting: "get('greeting') + ' ' + name"
```

### format()

Render a template string using the current operation context:

```yaml
dyngle:
  values:
    first-name: Alice
    last-name: Smith
  operations:
    greet:
      expressions:
        full-greeting: "format('Hello, {{first-name}} {{last-name}}!')"
      steps:
        - echo "{{full-greeting}}"
```

The `format()` function supports all template syntax, including nested properties:

```yaml
dyngle:
  operations:
    weather-report:
      expressions:
        report: "format('Temperature in {{location.city}} is {{weather.temperature}} degrees')"
      steps:
        - echo "{{report}}"
```

### dtformat()

Format datetime objects as strings using Python's `str.format()` with named components. Available components: `year`, `month`, `day`, `hour`, `minute`, `second`, `microsecond`, `weekday`.

```yaml
dyngle:
  expressions:
    now: "datetime.now()"
    timestamp: "dtformat(get('now'), '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}')"
  operations:
    log:
      steps:
        - echo "[{{timestamp}}] Event occurred"
```

The default format (when no format string is provided) is `{year:04d}{month:02d}{day:02d}`, producing output like `20260404`.

### PurePath()

Work with operating system paths:

```yaml
dyngle:
  operations:
    git-dir:
      expressions:
        result: PurePath(cwd) / '.git'
      steps:
        - pwd => cwd
      returns: result   
```

Note that command steps can be used for I/O operations while using Python to manipulate paths and strings.

```yaml
dyngle:
  operations:
    show-tests:
      expressions:
        test-dir: PurePath(cwd) / 'test'
        test-files: '[f.strip() for f in test_files_text.split("\n")]'
        result:
          test-dir: get('test-dir')
          test-files: get('test-files')
      steps:
        - pwd => cwd
        - ls -1 {{test-dir}} => test-files-text
      returns: result   
```

## Runtime Declarations

Runtime declarations are automatically provided values that reflect runtime execution context. Unlike constants and expressions defined in your configuration, these are set by the Dyngle runtime based on how the operation was invoked.

### runtime.args

Command-line arguments passed to `dyngle run` are available under `runtime.args`:

```yaml
dyngle:
  operations:
    greet:
      expressions:
        name: "get('runtime.args.0') or 'World'"
      steps:
        - echo "Hello {{name}}!"
```

Run with:

```bash
dyngle run greet Alice
```

Output:

```text
Hello Alice!
```

**Important notes:**
- `runtime.args` is only available in the `run` command, not in MCP operations
- Args are not automatically passed to sub-operations; use `send:` to pass them explicitly
- Access via `get('runtime.args.N')` for safe access with defaults
- Access via `runtime.args.N` in templates when you know the arg exists

The `runtime` namespace is reserved for future runtime-provided values (environment info, execution metadata, etc.).

## Environment and System Functions

### getenv()

Access environment variables:

```yaml
dyngle:
  operations:
    show-env:
      expressions:
        home-dir: "getenv('HOME', '/default/path')"
        api-key: "getenv('API_KEY') or 'not-set'"
      steps:
        - 'echo "Home directory: {{home-dir}}"'
        - 'echo "API Key: {{api-key}}"'
```

### getcwd()

Get the current working directory:

```yaml
dyngle:
  operations:
    show-cwd:
      expressions:
        current-dir: "getcwd()"
        parent-dir: "str(PurePath(getcwd()).parent)"
      steps:
        - 'echo "Working in: {{current-dir}}"'
        - 'echo "Parent: {{parent-dir}}"'
```

## Data Serialization Functions

### to_json()

Convert Python data structures to JSON strings:

```yaml
dyngle:
  operations:
    create-config:
      expressions:
        config-data:
          server: "format('{{host}}')"
          port: "int(get('port'))"
          enabled: "True"
        json-output: "to_json(get('config-data'))"
      steps:
        - echo "{{json-output}}"
```

### from_json()

Parse JSON strings into Python data structures:

```yaml
dyngle:
  operations:
    parse-json:
      expressions:
        parsed: "from_json(json_string)"
        server-host: "get('parsed')['server']"
      steps:
        - 'echo "Server: {{server-host}}"'
```

### to_yaml()

Convert Python data structures to YAML strings:

```yaml
dyngle:
  operations:
    create-yaml:
      expressions:
        config-data:
          database: "format('{{db-name}}')"
          timeout: "30"
        yaml-output: "to_yaml(get('config-data'))"
      steps:
        - echo "{{yaml-output}}"
```

### from_yaml()

Parse YAML strings into Python data structures:

```yaml
dyngle:
  operations:
    parse-yaml:
      expressions:
        parsed: "from_yaml(yaml_string)"
        db-name: "get('parsed')['database']"
      steps:
        - 'echo "Database: {{db-name}}"'
```

## Python Features

Expressions support a subset of Python's features:

### Built-in Types and Functions

- `str()`, `int()`, `float()`, `bool()`, `len()`, etc.

### Standard Library Modules

- **datetime** - Date and time operations (`datetime.now()`, `datetime.now().date()`, etc.)
- **math** - Mathematical functions (`math.pi`, `math.sqrt()`, etc.)
- **re** - Regular expression operations (`re.match()`, `re.search()`, `re.sub()`, etc.)
- **PurePath()** - Path manipulation operations (no file I/O)
- **json** - JSON serialization via `to_json()` and `from_json()` functions
- **yaml** - YAML serialization via `to_yaml()` and `from_yaml()` functions
- **os** - Environment and system operations via `getenv()` and `getcwd()` functions

### Data Structures

- Lists, dictionaries, tuples
- List comprehensions
- Dictionary comprehensions

### Operators

- **Arithmetic**: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical**: `and`, `or`, `not`
- **String**: concatenation, formatting

## Expression Examples

### String Manipulation

```yaml
dyngle:
  expressions:
    uppercase-name: "name.upper()"
    initials: "'.'.join([word[0] for word in name.split()])"
```

### Mathematical Operations

```yaml
dyngle:
  expressions:
    circle-area: "math.pi * radius ** 2"
    rounded: "round(get('circle-area'), 2)"
```

### Date and Time

```yaml
dyngle:
  expressions:
    now: "datetime.now()"
    today: "get('now').date()"
    formatted-date: "dtformat(get('now'), '{year:04d}-{month:02d}-{day:02d}')"
```

### List Operations

```yaml
dyngle:
  values:
    numbers: [1, 2, 3, 4, 5]
  expressions:
    doubled: "[n * 2 for n in get('numbers')]"
    sum-numbers: "sum(get('numbers'))"
    max-number: "max(get('numbers'))"
```

### Conditional Logic

```yaml
dyngle:
  expressions:
    environment: "get('env') if get('env') else 'development'"
    log-level: "'DEBUG' if get('environment') == 'development' else 'INFO'"
```

## Nested Structure Syntax

Constants and expressions can contain YAML structures. This allows defining hierarchical data that can be referenced using context paths.

### For Constants

Use nested YAML structures directly:

```yaml
dyngle:
  constants:
    server:
      host: api.example.com
      port: 443
      ssl: true
    database:
      name: mydb
      connection:
        - host: db.example.com
        - port: 5432
  operations:
    connect:
      steps:
        - echo "Connecting to {{server.host}}:{{server.port}}"
        - 'echo "Database: {{database.name}}"'
```

### For Expressions

Strings within YAML structures can be referenced and evaluated as separate expression:

```yaml
dyngle:
  expressions:
    configure:
      server:
        host: "format('{{server-host}}')"
        port: "int(get('server-port'))"
      database:
        name: "format('{{db-name}}')"
        connection:
          - "format('{{db-host}}')"
          - "int(get('db-port'))"
```

### Important Notes

- Each string in an expression structure is evaluated as Python code
- Numbers, booleans, and None pass through unchanged in both constants and expressions
- For string literals in expressions, use Python string syntax: `"'literal string'"`
- Access nested properties using context paths: `{{config.server.host}}`
- Access array elements in expressions using Python brackets: `get('coordinates')[get('location-index')]`

### Mixed Example

Combining constants and expressions with nested structures:

```yaml
dyngle:
  constants:
    defaults:
      timeout: 30
      retries: 3
  expressions:
    runtime:
      timestamp: "datetime.now()"
      timeout: "get('defaults'.timeout') * 2"
      config:
        retry-count: "get('defaults.retries')"
        enabled: "True"
  operations:
    process:
      steps:
        - 'echo "Timeout: {{runtime.timeout}}"'
        - 'echo "Retries: {{runtime.config.retry-count}}"'
```

## Context paths

Both constants and expressions with nested structures can be accessed using context paths in:

- **Templates**: `{{config.server.host}}`
- **Expressions**: `get('config.server.host')` or via variables if hyphen-free
- **`returns:`**: `config.server.host`

```yaml
dyngle:
  constants:
    api:
      endpoint: https://api.example.com
      version: v1
  operations:
    call-api:
      returns: api.endpoint
      expressions:
        full-url: "get('api.endpoint') + '/' + get('api.version')"
      steps:
        - echo "Calling {{full-url}}"
```

## Next Steps

- [Learn about sub-operations](sub-operations.md)
- [Understand operation context](operation-context.md)
- [Explore output modes](output-modes.md)
