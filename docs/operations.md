# Operations

Operations are the fundamental building blocks in Dyngle. An operation is a named sequence of steps that execute commands, and/or a set of expressions to evaluate in realtime.

## Basic Structure

Operations are defined under `dyngle:` in the configuration. The simplest form is a YAML array of command steps:

```yaml
dyngle:
  operations:
    hello:
      - echo "Hello world"
    
    build:
      - npm install
      - npm run build
```

Run an operation:

```bash
dyngle run hello
```

## Operation Definition

When you need additional attributes beyond just steps, use the extended form with a `steps:` key:

```yaml
dyngle:
  operations:
    build:
      description: Build the project for production
      access: public
      returns: build-info
      expressions:
        build-time: "datetime.now()"
      steps:
        - npm install
        - npm run build
        - echo "{{build-time}}" => build-info
```

### Omitting steps:

The `steps:` attribute is optional if all you need is expressions. This is convenient for simple operations that compute and return values without executing commands:

```yaml
dyngle:
  operations:
    get-timestamp:
      returns: timestamp
      expressions:
        timestamp: "dtformat(datetime.now(), '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}')"
```

Note that there are two kinds of steps - details in later sections:
- **Command steps** (the default) - Execute system commands
- **Sub-operation steps** - Call other operations

## Operation Attributes

### description

An optional description that appears in `dyngle list-operations` output:

```yaml
dyngle:
  operations:
    deploy:
      description: Deploy to production
      steps:
        - sub: build
        - aws s3 sync ./dist s3://my-bucket/
```

### access

Controls visibility and usage of operations.

**public (default)**

Public operations can be:
- Run directly via `dyngle run`
- Exposed as tools through the MCP server
- Listed in `dyngle list-operations` output

```yaml
dyngle:
  operations:
    deploy:
      access: public  # Explicitly public (default if omitted)
      description: Deploy to production
      steps:
        - sub: build
        - aws s3 sync ./dist s3://my-bucket/
```

If `access:` is not specified, operations default to `public`.

**private**

Private operations can **only** be called as sub-operations by other operations. They cannot be:
- Run directly via `dyngle run` (will fail with an error)
- Exposed through the MCP server
- Listed in `dyngle list-operations` output

```yaml
dyngle:
  operations:
    build:
      access: private
      steps:
        - npm install
        - npm run build
    
    deploy:
      steps:
        - sub: build  # OK - called as sub-operation
        - aws s3 sync ./dist s3://my-bucket/
```

Use private operations for:
- Helper operations that shouldn't be run directly
- Operations that handle secrets
- Internal implementation details
- Components of larger workflows

### returns

Specifies what value to return. See [Output modes](output-modes.md) for details.

```yaml
dyngle:
  operations:
    get-temperature:
      returns: temp
      steps:
        - curl -s "https://api.example.com/weather" => weather-data
        - weather-data -> jq -r '.temperature' => temp
```

### accepts

Defines a schema to validate and default input data. When specified, inputs (from stdin, `send:`, or JSON via MCP) are validated before execution.

**Basic example:**

```yaml
dyngle:
  operations:
    greet-user:
      accepts:
        name: { type: string }
        age: { type: integer }
      steps:
        - echo "Hello {{name}}, age {{age}}"
```

The `accepts:` attribute creates a contract for your operation, ensuring it receives the expected data structure. See [Inputs and interfaces](inputs-and-interfaces.md) for complete syntax and validation details.

### expressions

Local expressions available only within this operation. See [Constants and expressions](constants-and-expressions.md) for details.

```yaml
dyngle:
  operations:
    greet:
      expressions:
        greeting: "'Hello ' + name + '!'"
      steps:
        - echo "{{greeting}}"
```

### values

Local values (constants) available only within this operation. See [Constants and expressions](constants-and-expressions.md) for details.

```yaml
dyngle:
  operations:
    deploy:
      constants:
        environment: production
        region: us-west-2
      steps:
        - echo "Deploying to {{environment}} in {{region}}"
```

## Operation Inputs

Inputs are values that enter an operation from outside. There are three ways inputs are provided to an operation:

### Via stdin (in the run command)

Pass YAML data through stdin:

```bash
echo "name: Alice\nage: 30" | dyngle run greet-user
```

### Via send: (in sub-operations)

Parent operations can pass data to sub-operations:

```yaml
dyngle:
  operations:
    child:
      accepts:
        name: { type: string }
      steps:
        - echo "Hello {{name}}"
    
    parent:
      constants:
        user-data:
          name: Bob
      steps:
        - sub: child
          send: user-data
```

See [Sub-operations](sub-operations.md) for details.

### Via JSON (through MCP)

When operations are called through the MCP server, inputs are provided as JSON:

```json
{
  "tool": "greet-user",
  "name": "Alice",
  "age": 30
}
```

See [MCP Server](mcp-server.md) for details.

## Examples

### Development workflow

```yaml
dyngle:
  operations:
    test:
      description: Run the test suite
      steps:
        - pytest --cov=src tests/
        - coverage report
    
    lint:
      description: Check code style
      steps:
        - black --check src/
        - flake8 src/
    
    ci:
      description: Run all checks
      steps:
        - sub: test
        - sub: lint
```

### Data processing

```yaml
dyngle:
  operations:
    process-data:
      returns: result
      steps:
        - curl -s "https://api.example.com/data" => raw-data
        - raw-data -> jq '.items' => filtered
        - filtered -> python process.py => result
```

## Next Steps

- [Learn about command steps](command-steps.md)
- [Understand operation context](operation-context.md)
- [Explore inputs and interfaces](inputs-and-interfaces.md)
- [Review best practices](best-practices.md)
