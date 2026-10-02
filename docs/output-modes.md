# Output Modes

Operations behave differently depending on whether they have a `returns:` key. This determines how output is handled and displayed.

## The Two Modes

### Script Mode (without `returns:`)

Operations without `returns:` behave like shell scripts - all command stdout goes to stdout:

```yaml
dyngle:
  operations:
    build:
      - echo "Starting build..."
      - npm install
      - npm run build
      - echo "Build complete!"
```

All output is visible, making these ideal for build, deploy, and other workflow tasks where you want to see progress.

### Function Mode (with `returns:`)

Operations with `returns:` behave like functions - command stdout is suppressed, and only the return value is provided as output:

```yaml
dyngle:
  operations:
    get-temperature:
      returns: temp
      steps:
        - echo "Fetching weather..."  # stdout suppressed
        - curl -s "https://api.example.com/weather" => weather-data
        - weather-data -> jq -r '.temperature' => temp
```

Only the return value is output, making these ideal for data queries and transformations.

**Important:** 
- stderr is always displayed in both modes
- The `=>` operator works in both modes (capturing stdout to a variable)

## Output Destinations

Where the output goes depends on how the operation is invoked.

### In the run Command

When running an operation with `dyngle run`, output goes to stdout.

**Script mode** - All command stdout is displayed:

```bash
dyngle run build
```

Output:

```text
Starting build...
[npm install output...]
[npm run build output...]
Build complete!
```

**Function mode** - Only the return value is displayed:

```bash
dyngle run get-temperature
```

Output:

```text
72
```

**Output formatting** depends on the return value type:

- Simple types (strings, numbers, booleans) - Printed as-is
- Dictionaries and lists - Formatted as YAML

Example with structured data:

```yaml
dyngle:
  operations:
    get-user:
      returns: user
      steps:
        - curl -s "https://api.example.com/user/123" => user
```

```bash
dyngle run get-user
```

Output:

```yaml
name: Alice Smith
email: alice@example.com
role: admin
```

### In Sub-operations

When an operation is called as a sub-operation, its return value is captured by the parent's `receive:` attribute:

```yaml
dyngle:
  operations:
    get-version:
      returns: version
      steps:
        - cat package.json -> jq -r '.version' => version
    
    tag-release:
      steps:
        - sub: get-version
          receive: ver
        - git tag "v{{ver}}"
        - git push origin "v{{ver}}"
```

The return value becomes a variable in the parent operation's context.

**If no `returns:` is specified**, `receive:` captures `None`.

### In the MCP Server

When operations are exposed via the MCP server, they return JSON responses.

**Success with return value:**

```yaml
dyngle:
  operations:
    get-weather:
      description: Get current weather for a city
      returns: weather-info
      accepts:
        city: { type: string }
      steps:
        - curl -s "https://api.example.com/weather?city={{city}}" => weather-info
```

Response:

```json
{
  "result": {
    "temperature": 72,
    "conditions": "Sunny",
    "humidity": 65
  }
}
```

**Success without return value:**

```yaml
dyngle:
  operations:
    run-backup:
      description: Run the nightly backup process
      steps:
        - /usr/local/bin/backup.sh
```

Response:

```json
{
  "result": null
}
```

**Error:**

```json
{
  "error": "Operation failed: command not found"
}
```

This makes operations with return values particularly useful as AI assistant tools - they can return structured data that assistants can incorporate into responses.

## Specifying Return Values

Use the `returns:` key to specify what value to return:

```yaml
dyngle:
  operations:
    get-temperature:
      returns: temp
      steps:
        - curl -s "https://api.example.com/weather" => weather-data
        - weather-data -> jq -r '.temperature' => temp
```

The `returns:` key can reference anything in the operation context using context paths:

- Variables (set via `=>` or `receive:`)
- Constants (from `constants:`)
- Expressions (from `expressions:`)
- Inputs (from stdin, `send:`, or MCP)
- Nested properties (using dot-separated context paths)

Examples:

```yaml
dyngle:
  operations:
    # Return a variable
    fetch-data:
      returns: data
      steps:
        - curl -s "https://api.example.com" => data
    
    # Return a constant
    get-env:
      returns: environment
      constants:
        environment: production
    
    # Return an expression
    get-timestamp:
      returns: timestamp
      expressions:
        timestamp: "dtformat(datetime.now(), '{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}')"
    
    # Return nested property
    get-host:
      returns: config.server.host
      constants:
        config:
          server:
            host: api.example.com
            port: 443
```

### Template Structures in returns:

The `returns:` key can also accept template structures, allowing you to construct return values inline:

```yaml
dyngle:
  operations:
    get-build-info:
      returns:
        version: $ver
        commit: $sha
        timestamp: "{{runtime.timestamp}}"
      steps:
        - cat version.txt => ver
        - git rev-parse HEAD => sha
```

You can use either `$variable` or `"{{variable}}"` syntax for template references.

This returns a dictionary with the specified structure. Template structures support:

- **String templates**: Use `{{...}}` syntax to reference context values
- **Non-string constants**: Include integers, booleans, and floats directly
- **Nested structures**: Create complex nested dictionaries and lists
- **Lists**: Return arrays of values

Example with nested structure:

```yaml
dyngle:
  operations:
    get-config:
      returns:
        app:
          name: $app-name
          version: $version
        server:
          host: $host
          port: 8080
          enabled: true
      constants:
        app-name: MyApp
        version: 1.0.0
        host: example.com
      steps:
        - echo "Gathering configuration..."
```

Example with list:

```yaml
dyngle:
  operations:
    get-tags:
      returns:
        - "{{app}}-{{version}}"
        - "{{app}}-latest"
        - "production"
      constants:
        app: myapp
        version: 2.0
      steps:
        - echo "Building tag list..."
```

This is equivalent to using expressions but more concise for structured data:

```yaml
# Equivalent to:
get-build-info:
  expressions:
    result:
      version: "{{ver}}"
      commit: "{{sha}}"
      timestamp: "{{runtime.timestamp}}"
  returns: result
  steps:
    - cat version.txt => ver
    - git rev-parse HEAD => sha
```

## Display Control

The `--display` option controls whether step commands are shown before execution, independently of output mode:

```bash
dyngle run build --display none
```

This suppresses step display but doesn't affect the mode (script vs function) or stdout handling.

See [CLI Commands](cli-commands.md) for details on the `--display` option.

## Examples

### Simple String Return

```yaml
dyngle:
  operations:
    get-version:
      returns: version
      steps:
        - cat package.json -> jq -r '.version' => version
```

```bash
dyngle run get-version
```

Output:

```text
1.2.3
```

### Structured Data Return

```yaml
dyngle:
  operations:
    system-info:
      returns: info
      expressions:
        info:
          hostname: "get('runtime.args.0') or 'localhost'"
          timestamp: "datetime.now()"
          user: "'admin'"
```

```bash
dyngle run system-info myserver
```

Output:

```yaml
hostname: myserver
timestamp: 2024-12-14 22:00:00
user: admin
```

### Computed Return Value

```yaml
dyngle:
  operations:
    calculate-total:
      returns: total
      steps:
        - curl -s "https://api.example.com/items" => items
        - items -> jq '[.[] | .price] | add' => total
```

### Workflow with No Return

```yaml
dyngle:
  operations:
    deploy:
      description: Deploy to production
      steps:
        - echo "Starting deployment..."
        - sub: build
        - aws s3 sync ./dist s3://my-bucket/
        - echo "Deployment complete!"
```

All output is visible during execution.

## Best Practices

### Use Function Mode for Data Operations

Operations that query or transform data should use `returns:`:

```yaml
dyngle:
  operations:
    get-status:
      description: Check deployment status
      returns: status
      steps:
        - curl -s "https://api.example.com/status" => status
```

### Use Script Mode for Workflows

Operations that perform tasks should omit `returns:`:

```yaml
dyngle:
  operations:
    deploy:
      description: Deploy application
      steps:
        - sub: build
        - sub: test
        - sub: upload
        - echo "Deployment complete!"
```

### Return Structured Data for MCP

Operations exposed via MCP should return meaningful structured data:

```yaml
dyngle:
  operations:
    check-health:
      description: Check application health
      returns: health
      steps:
        - curl -s "https://api.example.com/health" => health
```

This allows AI assistants to understand and use the returned information.

## Next Steps

- [Learn about MCP Server integration](mcp-server.md)
- [Understand operation context](operation-context.md)
- [Explore CLI commands](cli-commands.md)
