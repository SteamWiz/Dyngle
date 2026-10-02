# MCP Server

Dyngle can run as an MCP (Model Context Protocol) server, exposing operations as tools that AI assistants like Claude can execute.

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol that allows AI assistants to discover and use external tools. When Dyngle runs as an MCP server, your configured operations become tools that AI assistants can call to perform tasks.

## Starting the Server

Use the `mcp` command with the `--config` option to specify a configuration file:

```bash
dyngle --config ./.dyngle.mcp.yml mcp
```

This starts a server using the `stdio` (standard input/output) transport, which is ideal for integration with Claude Desktop and other AI assistants that support local MCP servers.

**Recommended convention:** Use `.dyngle.mcp.yml` as your MCP-specific configuration file to separate MCP-exposed operations from your regular workflow operations.

### Filtering Operations

Use the `--operations` option to selectively expose only specific operations as MCP tools:

```bash
dyngle --config ./.dyngle.mcp.yml mcp --operations op1,op2,op3
```

This is useful when:
- You have many operations but only want to expose a subset via MCP
- You want different MCP server instances exposing different operations
- You need to restrict which operations are available to AI assistants

**Example:** Expose only read-only operations:

```bash
dyngle --config ./.dyngle.mcp.yml mcp --operations get-status,list-items,read-log
```

The option accepts a comma-separated list of operation keys. Whitespace around commas is ignored. If any operation key is not found in the configuration, the command will fail with an error before starting the server.

If `--operations` is not specified, all public operations are exposed (the default behavior).

## Passing Arguments to Operations

You can pass positional arguments when starting the MCP server. These arguments are available to all operations throughout the session:

```bash
dyngle --config ./.dyngle.mcp.yml mcp arg1 arg2 arg3
```

Operations can access these arguments via the `args` list in expressions:

```yaml
dyngle:
  expressions:
    first_arg: "args[0]"
    second_arg: "args[1]"
  operations:
    process-with-args:
      description: Process data using session arguments
      accepts:
        input: { type: string }
      returns: result
      steps:
        - echo "Processing {{input}} with {{first_arg}} and {{second_arg}}" => result
```

### Use Cases

**Environment-specific configuration:**
```bash
# Development
dyngle --config ./.dyngle.mcp.yml mcp dev localhost:3000

# Production
dyngle --config ./.dyngle.mcp.yml mcp prod api.example.com
```

**Shared credentials or tokens:**
```bash
dyngle --config ./.dyngle.mcp.yml mcp $API_TOKEN
```

### Claude Desktop Configuration with Arguments

```json
{
  "mcpServers": {
    "myapp-dev": {
      "command": "dyngle",
      "args": ["--config", "/path/to/.dyngle.mcp.yml", "mcp", "dev", "localhost:3000"]
    },
    "myapp-prod": {
      "command": "dyngle",
      "args": ["--config", "/path/to/.dyngle.mcp.yml", "mcp", "prod", "api.example.com"]
    }
  }
}
```

This allows you to run multiple instances of the same MCP server with different configurations.

## How Operations Become Tools

When the MCP server starts:

1. Each **public** operation becomes an MCP tool
2. **Private** operations are not exposed
3. Tool input parameters depend on the operation's `accepts:` definition:
   - **With accepts:** The accept fields become the tool's input parameters
   - **Without accepts:** The tool has no input parameters

### Tool Response Format

Tools return JSON responses:

**Success:**

```json
{"result": <value>}
```

Where `<value>` is the operation's return value (if specified), or `null` if no return value.

**Failure:**

```json
{"error": "<message>"}
```

### Example: Operation with Interface

```yaml
dyngle:
  operations:
    get-weather:
      description: Get current weather for a city
      accepts:
        city:
          type: string
      returns: weather-info
      steps:
        - curl -s "https://api.example.com/weather?city={{city}}" => weather-info
```

An AI assistant can call this tool with the interface parameters:

```json
{
  "tool": "get-weather",
  "city": "San Francisco"
}
```

And receive:

```json
{
  "result": {
    "temperature": 72,
    "conditions": "Sunny",
    "humidity": 65
  }
}
```

### Example: Operation without Interface

```yaml
dyngle:
  operations:
    run-backup:
      description: Run the nightly backup process
      returns: result
      steps:
        - /usr/local/bin/backup.sh => result
```

An AI assistant can call this tool with no parameters:

```json
{
  "tool": "run-backup"
}
```

## Configuring Claude Desktop

To use Dyngle operations with Claude Desktop, configure the MCP server in Claude's configuration file.

### macOS Configuration

Edit or create `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dyngle": {
      "command": "dyngle",
      "args": ["--config", "/absolute/path/to/your/project/.dyngle.mcp.yml", "mcp"]
    }
  }
}
```

**Important:**
- Use absolute paths for the configuration file
- Restart Claude Desktop completely after editing (not just close the window)
- Tools appear in Claude's "Search and tools" interface

### Example with Project-Specific Config

For a project at `/Users/alice/projects/myapp`:

```json
{
  "mcpServers": {
    "myapp": {
      "command": "dyngle",
      "args": ["--config", "/Users/alice/projects/myapp/.dyngle.mcp.yml", "mcp"]
    }
  }
}
```

### Configuration File Search

If you don't specify a `--config` option, Dyngle follows the standard configuration file search order. See [Configuration](configuration.md#configuration-file-location) for details. However, it's recommended to always use `--config` with MCP to ensure the correct operations are exposed.

## Design Considerations

### Use Descriptions and Interfaces

Operations exposed via MCP should have clear descriptions and, where appropriate, explicit interface definitions:

```yaml
dyngle:
  operations:
    deploy-app:
      description: Deploy the application to a specified environment
      accepts:
        environment:
          type: string
        version:
          type: string
      steps:
        - sub: build
        - aws s3 sync ./dist s3://{{environment}}-bucket/{{version}}/
```

The description helps AI assistants understand when to use the tool, and the interface makes the expected inputs explicit. See [Operations](operations.md) for full interface syntax details.

### Return Values and Interfaces

Operations used as tools should return meaningful values and use interfaces to define expected inputs:

```yaml
dyngle:
  operations:
    check-status:
      description: Check deployment status
      accepts:
        service:
          type: string
      returns: status
      steps:
        - curl -s "https://api.example.com/status?service={{service}}" => status
```

This allows AI assistants to understand what inputs are needed and incorporate the result into their responses.

### Private Operations for Secrets

Use private operations to protect sensitive operations:

```yaml
dyngle:
  operations:
    get-credentials:
      access: private
      returns: creds
      steps:
        - aws secretsmanager get-secret-value --secret-id api-creds => creds
    
    make-api-call:
      description: Call the API with authentication
      steps:
        - sub: get-credentials
          receive: creds
        - curl -H "Authorization: {{creds}}" https://api.example.com/data
```

The `get-credentials` operation won't be exposed to AI assistants.

## Example Configuration

Create a `.dyngle.mcp.yml` file with operations designed for AI assistant use:

```yaml
dyngle:
  operations:
    # Development workflow
    run-tests:
      description: Run the test suite for a specific module
      accepts:
        module: { type: string }
      returns: test-results
      steps:
        - pytest {{module}} --json-report => results
        - results -> jq '.summary' => test-results
    
    # Information queries
    get-version:
      description: Get version from package.json
      accepts:
        package: { type: string }
      returns: version
      steps:
        - cat {{package}}/package.json => pkg
        - pkg -> jq -r '.version' => version
    
    # System operations
    check-service:
      description: Check the status of a specific application service
      accepts:
        service: { type: string }
      returns: status
      steps:
        - systemctl status {{service}} => output
        - echo "Service {{service}} is running" => status
```

See [Use Cases](use-cases.md) for more examples of operations suitable for MCP integration.

## Troubleshooting

### Server Not Showing Up

1. **Check JSON syntax** - Validate `claude_desktop_config.json`
2. **Verify Dyngle in PATH** - Run `which dyngle` (macOS/Linux) or `where dyngle` (Windows)
3. **Use full path** - Try the full path to the dyngle executable in the `command` field
4. **Restart Claude Desktop** - Use Cmd+Q (macOS) or quit from system tray (Windows)

### Checking Logs (macOS)

Claude Desktop writes logs to `~/Library/Logs/Claude/`:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
```

## Next Steps

- [Explore use cases](use-cases.md)
- [Understand output modes](output-modes.md)
- [Learn about inputs and interfaces](inputs-and-interfaces.md)
