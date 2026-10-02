# Operation Context

The operation context is all of the information available within an operation for use in templates, expressions, `return:`, and other places. Understanding the context is key to building effective operations.

## What is Context?

**Context** encompasses all named values accessible within an operation, regardless of how they're defined or populated. The context includes:

- **Constants** - Defined with `constants:`
- **Expressions** - Defined with `expressions:`
- **Inputs** - Data entering the operation from outside
- **Variables** - Values set during execution with `receive:` or `=>`

## Inputs

**Inputs** are values that enter the operation from outside sources. There are three ways inputs are provided:

### Via stdin (in the run command)

Pass YAML data through stdin:

```bash
echo "name: Alice" | dyngle run hello
```

### Via send: (in sub-operations)

Parent operations pass data to sub-operations:

```yaml
dyngle:
  operations:
    child:
      steps:
        - echo "Hello {{name}}"
    
    parent:
      constants:
        data:
          name: Bob
      steps:
        - sub: child
          send: data  # 'name' becomes an input to child
```

### Via JSON (through MCP)

When called through the MCP server, inputs are provided as JSON:

```json
{
  "tool": "greet-user",
  "name": "Alice"
}
```

### Via command-line arguments

Command-line arguments passed to `dyngle run` are available as the `runtime.args` list:

```bash
dyngle run greet Alice Bob Charlie
```

Note that `runtime.args` is not available directly to sub-commands; values must be passed explicitly.

## Variables

**Variables** are values set during operation execution. They're created in two ways:

### Using the receive operator (=>)

Capture command stdout:

```yaml
dyngle:
  operations:
    fetch-data:
      steps:
        - curl -s "https://api.example.com/users" => users  # 'users' is a variable
        - echo "Fetched: {{users}}"
```

### Using receive: in sub-operations

Capture return values from sub-operations:

```yaml
dyngle:
  operations:
    get-version:
      returns: ver
      steps:
        - cat package.json -> jq -r '.version' => ver
    
    tag-release:
      steps:
        - sub: get-version
          receive: version  # 'version' is a variable
        - git tag "v{{version}}"
```

Variables have the highest precedence in the context (see below).

## Constants and Expressions from Configuration

The context also includes values and expressions defined in your configuration:

### Global

```yaml
dyngle:
  constants:
    environment: production
  expressions:
    timestamp: "datetime.now()"
  operations:
    deploy:
      steps:
        - echo "Deploying to {{environment}} at {{timestamp}}"
```

### Local (operation-specific)

```yaml
dyngle:
  operations:
    deploy:
      constants:
        region: us-west-2
      expressions:
        build-time: "datetime.now()"
      steps:
        - echo "Deploying to {{region}} at {{build-time}}"
```

See [Constants and expressions](constants-and-expressions.md) for details.

## Context Key Precedence

When names overlap, Dyngle resolves them using this precedence (highest to lowest):

1. **Variables** (populated via `=>` operator or `receive:`) within the operation
2. **Local expressions and constants** (defined in the operation)
3. **Global expressions and constants** (defined under `dyngle:`)
6. **Inputs** (from stdin, `send:`, or MCP JSON)

(Expressions and constants together are also called "declarations".)

Example:

```yaml
dyngle:
  constants:
    name: Global
  expressions:
    name: "'Expression'"
  operations:
    test:
      constants:
        name: Local
      steps:
        - echo "Start: {{name}}"        # "Local" (local constant wins)
        - echo "Override" => name
        - echo "After: {{name}}"         # "Override" (variable wins)
```

## Real-time Evaluation

Expressions are evaluated in real-time based on the current state of the context. This means:

- When an expression references another value, it uses the current value at evaluation time
- Variables created during execution are immediately available to subsequent expressions
- Changes to the context during execution affect expression results

Example:

```yaml
dyngle:
  operations:
    demo:
      expressions:
        message: "format('Count is {{count}}')"
      steps:
        - echo "5" => count
        - echo "{{message}}"        # "Count is 5"
        - echo "10" => count
        - echo "{{message}}"        # "Count is 10"
```

## Accessing Context Values

Everything in the context can be referenced using context paths in these places:

### In Templates

Use `{{variable}}` syntax in command steps:

```yaml
- echo "Hello {{name}}!"
- 'echo "Temperature: {{weather.temperature}}"'
```

### In Expressions with get()

Use the `get()` function to access context constants:

```yaml
dyngle:
  expressions:
    full-greeting: "'Hello ' + get('name')"
    temp: get('weather.temperature')
```

### In returns:

Specify which context value to return:

```yaml
dyngle:
  operations:
    get-temperature:
      returns: temp
      steps:
        - curl -s "https://api.example.com/weather" => weather-data
        - weather-data -> jq -r '.temperature' => temp
```

The `returns:` key can reference:
- Variables (set via `=>` or `receive:`)
- Constants (from `constants:`)
- Expressions (from `expressions:`)
- Inputs (from stdin, `send:`, or MCP)

Essentially, `returns:` can access anything in the operation context using the same key names.

## Nested Object Properties

Access nested properties in dictionaries using context paths:

```yaml
dyngle:
  operations:
    weather-report:
      steps:
        - curl -s "https://api.example.com/weather" => weather
        - 'echo "Temperature: {{weather.temperature}}"'
        - 'echo "Location: {{weather.location.city}}, {{weather.location.country}}"'
```

### Working with Arrays

For arrays, use expressions to extract constants:

```yaml
dyngle:
  constants:
    users:
      - name: Alice
        email: alice@example.com
      - name: Bob
        email: bob@example.com
  operations:
    show-users:
      expressions:
        first-user: get('users')[0]
        first-name: get('users')[0]['name']
        all-names: "[u['name'] for u in get('users')]"
      steps:
        - echo "First user: {{first-name}}"
```

## Context Scope

Each operation maintains its own context. When using sub-operations:

- Parent and child contexts are isolated by default
- Use `send:` to explicitly pass data to a child
- Use `receive:` to explicitly capture data from a child

See [Sub-operations](sub-operations.md) for details on context scope with sub-operations.

## Example: Context Evolution

Here's how context evolves during execution:

```yaml
dyngle:
  constants:
    base: Global constant
  expressions:
    computed: "'Global expression'"
  operations:
    demo:
      constants:
        local: Local constant
      expressions:
        derived: "'Derived: ' + get('local')"
      steps:
        - echo "{{base}}"           # Global constant
        - echo "{{computed}}"        # Global expression
        - echo "{{local}}"           # Local constant
        - echo "{{derived}}"         # Local expression
        - echo "Runtime" => dynamic  # Creates variable
        - echo "{{dynamic}}"         # Variable
```

Context at different points:

1. **Start**: `{base, computed, local, derived}`
2. **After step 5**: `{base, computed, local, derived, dynamic}`

## Next Steps

- [Learn about inputs and interfaces](inputs-and-interfaces.md)
- [Explore constants and expressions](constants-and-expressions.md)
- [Understand sub-operations](sub-operations.md)
