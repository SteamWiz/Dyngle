# Command Steps

Command steps are the default type of operation step in Dyngle. They execute system commands directly, without using a shell.

## Not a Shell

**Important:** Operation steps use shell-like syntax but are **not** executed in a shell. Commands are parsed and executed directly by Python's `subprocess.run()`.

This means shell-specific features won't work:

**Doesn't work (shell syntax):**

```yaml
- echo "Hello" | grep Hello  # Use data flow operators instead
- export VAR=value           # Use expressions or values instead
- ls > files.txt             # Use data flow operators instead
- cd /some/path && ls        # Each step is independent
```

**Works (Dyngle syntax):**

```yaml
- echo "Hello world"
- npm install
- python script.py --arg value
- curl -s "https://api.example.com/data"
```

Use Dyngle's features for data flow, variable substitution, and composability instead of shell features.

## Template Syntax

Use double-curly-bracket syntax (`{{` and `}}`) to inject values from the operation context into commands:

```yaml
dyngle:
  operations:
    hello:
      - echo "Hello {{name}}!"
```

Templates are rendered before the command executes, replacing `{{variable}}` with the value from the operation context.

### Using Templates

The initial context used for command steps may come from YAML over stdin to the Dyngle run command.

```bash
echo "name: Francis" | dyngle run hello
```

Output:

```text
Hello Francis!
```

### Nested Properties

The double-brackets may contain a context path, using dot-separated strings and ints to navigate nested dicts and lists.

```yaml
dyngle:
  operations:
    weather-report:
      steps:
        - curl -s "https://api.example.com/weather" => weather
        - 'echo "Temperature: {{weather.temperature}}"'
        - 'echo "Location: {{weather.location.city}}, {{weather.location.country}}"'
```

```yaml
dyngle:
  constants:
    python-command: /bin/python3
  expressions:
    unittest-command: format('{{python-command}}) -m unittest').split()
  operations:
    test:
      - '{{unittest-command.0}} {{unittest-command.1}} {{unittest-command.2}} test/*'
```



### YAML type inference

YAML type inference impacts how Dyngle configurations are parsed. For example, if a string contains a colon, the YAML parser might interpret the content to the left of the colon as an object key.

```yaml
- echo 'Temperature: {{temperature}}' => data  # YAML parsing error!
```

One solution is to enclose the entire string entry in single or double quotes.

```yaml
- "echo 'Temperature: {{temperature}}' => data"
```

Another is to use a YAML multiline string.

```yaml
- >-
  echo 'Temperature: {{temperature}}' => data
```

Remember that the YAML parser sends the entire string to Dyngle to parse, so the command and data flow operators must all occupy the same string entry in YAML.

## Data Flow Operators

Dyngle provides two operators to pass data between steps.

### The Send Operator (`->`)

The send operator passes a value from the operation context as stdin to a command:

```yaml
dyngle:
  operations:
    process-data:
      steps:
        - curl -s "https://api.example.com/data" => raw-data
        - raw-data -> jq '.items' => filtered
        - filtered -> python process.py
```

The value is passed to the command's standard input.

#### Automatic YAML Conversion

When using the send operator, values are automatically converted to YAML format before being passed to stdin:

- **Strings** are passed as-is without modification
- **Dicts and lists** are serialized to YAML format
- **Numbers and other types** are converted to their string representation

This makes it easy to pass structured data to commands that expect YAML input:

```yaml
dyngle:
  operations:
    process-config:
      constants:
        config:
          host: localhost
          port: 8080
          enabled: true
      steps:
        - config -> python process_config.py
```

The command receives:

```yaml
host: localhost
port: 8080
enabled: true
```

### The Receive Operator (`=>`)

The receive operator captures stdout from a command and assigns it to a named variable in the operation context:

```yaml
dyngle:
  operations:
    fetch-data:
      steps:
        - curl -s "https://api.example.com/users" => users
        - echo "Fetched: {{users}}"
```

The captured value becomes available for subsequent steps.

### Combining Operators

You can use both operators in a single step:

```yaml
<input-variable> -> <command> => <output-variable>
```

Example:

```yaml
dyngle:
  operations:
    weather:
      steps:
        - curl -s "https://api.example.com/weather" => weather-data
        - weather-data -> jq -j '.temperature' => temp
        - echo "Temperature: {{temp}} degrees"
```

### Operator Order

When using both operators, they must appear in this order:

1. Send operator (`->`) first
2. Command in the middle
3. Receive operator (`=>`) last

### Operator Spacing

Operators must be isolated with whitespace:

**Correct:**

```yaml
- command => output
- input -> command
- input -> command => output
```

**Incorrect:**

```yaml
- command=>output        # Missing spaces
- input->command         # Missing spaces
```

## Siilarity to Sub-operations

Note the similarity between these operators in command steps and the `send:` and `receive:` attributes in sub-operation steps:

**Command step:**
```yaml
- input-data -> command => output-data
```

**Sub-operation step:**
```yaml
- sub: operation-name
  send: input-data
  receive: output-data
```

Both follow the same pattern of sending input and receiving output. See [Sub-operations](sub-operations.md) for details.

## Practical Examples

### API Data Processing

```yaml
dyngle:
  operations:
    get-user-emails:
      returns: emails
      steps:
        - curl -s "https://api.example.com/users" => users
        - users -> jq -r '.[].email' => emails
```

### Multi-step Pipeline

```yaml
dyngle:
  operations:
    analyze-logs:
      returns: summary
      steps:
        - curl -s "https://logs.example.com/today" => logs
        - logs -> grep "ERROR" => errors
        - errors -> wc -l => error-count
        - echo "Found {{error-count}} errors" => summary
```

### Data Transformation

```yaml
dyngle:
  operations:
    transform-json:
      returns: result
      steps:
        - cat input.json => raw
        - raw -> jq '.data | map({id, name})' => transformed
        - transformed -> python format.py => result
```

## Important Notes

### Variables Created with =>

Values populated with the receive operator (`=>`) have the highest precedence in the operation context. They override values, expressions, and inputs with the same name.

See [Operation context](operation-context.md#context-key-precedence) for complete precedence rules.

### Working with Structured Data

When data flow captures structured data (JSON, YAML), use a context path to access nested properties in templates:

```yaml
dyngle:
  operations:
    weather:
      steps:
        - curl -s "https://api.example.com/weather" => weather-data
        - 'echo "Temperature: {{weather-data.temperature}}"'
        - 'echo "City: {{weather-data.location.city}}"'
```

```yaml
dyngle:
  operations:
    process-items:
      expressions:
        items: from_json(get('items-json'))
      steps:
        - curl -s "https://api.example.com/items" => items-json
        - echo 'The first item is called {{items.0.name}}'
```

### Using Expressions with Data Flow

You can reference captured data in expressions:

```yaml
dyngle:
  operations:
    process:
      expressions:
        message: "format('Processed {{count}} items')"
      steps:
        - curl -s "https://api.example.com/items" => items
        - items -> jq 'length' => count
        - echo "{{message}}"
```

## Dict Form and `ignore-errors`

By default, a command step that exits with a nonzero code raises an error and halts the operation. When a command is expected to sometimes exit nonzero — but the operation should continue anyway — use the dict form of a command step with `ignore-errors: true`.

### Syntax

```yaml
- command: <step string>
  ignore-errors: true
```

The `command:` value is parsed exactly like a string step, including `->` and `=>` operators.

### Example

`grep` exits with code `1` when it finds no matches. To capture the match count without aborting the operation when there are no matches:

```yaml
dyngle:
  operations:
    count-matches:
      returns: line-count
      steps:
        - mktemp => tmp
        - data -> tee {{tmp}}
        - command: grep -xc 'pattern' {{tmp}} => line-count
          ignore-errors: true
        - rm {{tmp}}
```

Without `ignore-errors: true`, the operation would fail whenever `grep` finds zero matches.

### Notes

- `ignore-errors` defaults to `false`; omitting it gives the normal fail-fast behaviour
- Output capture (`=>`) still works normally even when the exit code is nonzero
- All data-flow operators (`->` and `=>`) are supported in the `command:` value

## Prompt Steps

Prompt steps allow operations to pause and wait for user input, even when the operation receives data via stdin.

### Basic Syntax

Use the `prompt:` key to display a message and wait for user input:

```yaml
dyngle:
  operations:
    wait-for-user:
      steps:
        - prompt: "Press enter to continue"
        - echo "Continuing..."
```

### Capturing Input

Use the `receive:` attribute to capture the user's input into a variable:

```yaml
dyngle:
  operations:
    get-name:
      steps:
        - prompt: "Enter your name: "
          receive: user-name
        - echo "Hello {{user-name}}!"
```

The captured input becomes available in the operation context for use in subsequent steps.

### Template Support

Prompt messages support template substitution:

```yaml
dyngle:
  constants:
    app-name: "MyApp"
  operations:
    welcome:
      steps:
        - prompt: "Welcome to {{app-name}}! Press enter to start"
          receive: confirm
        - echo "Starting {{app-name}}..."
```

### How It Works

Prompt steps use WizLib's UI handler to access the terminal (TTY) directly. This means prompts work even when stdin is redirected for passing data to the operation:

```bash
echo "config: value" | dyngle run my-operation
```

The operation can receive YAML data via stdin AND prompt the user for input during execution.

### Use Cases

**Interactive confirmation:**

```yaml
dyngle:
  operations:
    deploy:
      steps:
        - echo "About to deploy to production"
        - prompt: "Type 'yes' to confirm: "
          receive: confirmation
        - echo "Deploying..." # Only if user confirmed
```

**Collecting user input:**

```yaml
dyngle:
  operations:
    setup:
      steps:
        - prompt: "Enter project name: "
          receive: project-name
        - prompt: "Enter author name: "
          receive: author
        - echo "Creating {{project-name}} by {{author}}"
```

**Pausing for review:**

```yaml
dyngle:
  operations:
    analyze:
      steps:
        - curl -s "https://api.example.com/data" => data
        - echo "{{data}}"
        - prompt: "Review the data above. Press enter to continue"
        - data -> python process.py
```

### Important Notes

**TTY Required:**
Prompt steps require a TTY (interactive terminal). They will fail in non-interactive environments like cron jobs or CI/CD pipelines unless those environments provide TTY access.

**stdin vs TTY:**
Operations can receive structured data via stdin (for YAML input) and still prompt users interactively. These are independent mechanisms:
- stdin: For passing data to operations
- TTY: For interactive user prompts

**receive: Behavior:**
When using `receive:`, the captured input:
- Can be an empty string if the user just presses enter
- Becomes available immediately in the operation context
- Has the same precedence as other variables created during execution

## Conditional Steps

Conditional steps allow operations to execute different steps based on boolean conditions.

### Basic Syntax

Use `if:`, `then:`, and optionally `else:` to create conditional blocks:

```yaml
dyngle:
  operations:
    deploy:
      expressions:
        is-production: "environment == 'production'"
      steps:
        - if: is-production
          then:
            - echo "Deploying to production"
          else:
            - echo "Deploying to staging"
```

### Structure

- **`if:`** - References a value from the context to evaluate as boolean
- **`then:`** - List of steps to execute when the condition is true
- **`else:`** - (Optional) List of steps to execute when the condition is false

### Condition Evaluation

The value referenced by `if:` is evaluated using Python's truthiness rules:

- `True`, non-zero numbers, non-empty strings/lists/dicts evaluate to true
- `False`, `None`, `0`, empty strings/lists/dicts evaluate to false

The condition is evaluated in the operation's context, which includes:
- Operation inputs (from stdin, `send:`, or MCP)
- Global constants and expressions
- Local constants and expressions
- Variables captured from previous steps (via `=>` or `receive:`)

### Examples

**Basic conditional:**

```yaml
dyngle:
  operations:
    check-env:
      expressions:
        is-prod: "env == 'production'"
      steps:
        - if: is-prod
          then:
            - echo "Production environment"
          else:
            - echo "Non-production environment"
```

**Without else block:**

```yaml
dyngle:
  operations:
    optional-cleanup:
      expressions:
        should-cleanup: "cleanup_enabled"
      steps:
        - echo "Running main task"
        - if: should-cleanup
          then:
            - echo "Cleaning up"
            - rm -rf temp/
```

**With variables from previous steps:**

```yaml
dyngle:
  operations:
    check-status:
      expressions:
        is-healthy: "status_code == '200'"
      steps:
        - curl -s -o /dev/null -w "%{http_code}" "{{url}}" => status-code
        - if: is-healthy
          then:
            - echo "Service is healthy"
          else:
            - echo "Service is unhealthy"
```

**With sub-operations:**

```yaml
dyngle:
  operations:
    validate:
      steps:
        - echo "data"
    process:
      expressions:
        needs-validation: "validate_required"
      steps:
        - if: needs-validation
          then:
            - sub: validate
              send: data
              receive: validated
            - echo "Validated: {{validated}}"
          else:
            - echo "Skipping validation"
```

**Nested conditionals:**

```yaml
dyngle:
  operations:
    deploy:
      expressions:
        is-production: "environment == 'production'"
        requires-approval: "deployment_type == 'major'"
      steps:
        - if: is-production
          then:
            - if: requires-approval
              then:
                - prompt: "Type 'yes' to approve: "
                  receive: approval
                - echo "Deploying with approval"
              else:
                - echo "Deploying without approval"
          else:
            - echo "Deploying to staging"
```

### Variable Scope

Variables created within `then:` or `else:` blocks (via `=>` or `receive:`) are available to subsequent steps in the operation, regardless of which branch executed:

```yaml
dyngle:
  operations:
    example:
      expressions:
        use-default: "value == ''"
      steps:
        - if: use-default
          then:
            - echo "default" => result
          else:
            - echo "{{value}}" => result
        - echo "Result: {{result}}"  # Available here
```

### All Step Types Supported

Conditional blocks support all step types:
- Command steps (with `->` and `=>` operators)
- Sub-operation steps (with `sub:`, `send:`, `receive:`)
- Prompt steps (with `prompt:`, `receive:`)
- Nested conditional steps

### Error Handling

If the value referenced by `if:` does not exist in the operation context, the operation will fail with an error indicating the missing reference.

## Next Steps

- [Understand operation context](operation-context.md)
- [Learn about sub-operations](sub-operations.md)
- [Explore constants and expressions](constants-and-expressions.md)
