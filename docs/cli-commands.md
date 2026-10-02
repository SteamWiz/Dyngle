# CLI Commands

Dyngle provides several commands for working with operations.

## run

Execute a named operation from your configuration.

### Syntax

```bash
dyngle run <operation-name> [optional arguments...]
```

### Examples

Basic execution:

```bash
dyngle run hello
```

Pass command-line arguments that become available throughout the entire operation tree:

```bash
dyngle run greet Alice Bob
```

The `run` command is unique in supporting positional command-line arguments, as a convenience for common desktop operations. They can be accessed using the `runtime.args` context path.

```yaml
dyngle:
  operations:
    greet:
      expressions:
        name: "get('runtime.args.0') or 'World'"
      steps:
        - echo "Hello {{name}}!"
```

With data from stdin:

```bash
echo "name: Alice" | dyngle run hello
```

With a specific config file:

```bash
dyngle --config /path/to/.dyngle.yml run deploy
```

### Options

**`--display <mode>`**

Control step display behavior:

- `steps` (default) - Show each step before executing
- `none` - Suppress step display for cleaner output

```bash
dyngle run build --display none
```

#### When to Use Each Mode

**Use `steps` mode when:**

- **Debugging operations** - See exactly what commands are being executed
- **Learning** - Understand what's happening during execution
- **Development** - Verify that template substitution is working correctly
- **Interactive use** - Get visual confirmation of progress

**Use `none` mode when:**

- **Scripting** - Cleaner output for parsing or processing
- **Production workflows** - Reduce noise in logs
- **Return value focused** - When you only care about the final result
- **Automated systems** - CI/CD environments where step display is unnecessary

#### Examples

**Development workflow with step display:**

```bash
dyngle run test --display steps
```

Useful for seeing exactly what test commands are being run.

**Production deployment with clean output:**

```bash
dyngle run deploy --display none
```

Keeps deployment logs focused on command output without displaying each step.

**Combining with return values:**

When an operation has a return value, `none` mode is particularly useful:

```yaml
dyngle:
  operations:
    get-version:
      returns: version
      steps:
        - cat package.json => pkg
        - pkg -> jq -r '.version' => version
```

With `steps` mode:

```bash
$ dyngle run get-version --display steps
```

Output:

```text
$ cat package.json => pkg
$ pkg -> jq -r '.version' => version
1.2.3
```

With `none` mode:

```bash
$ dyngle run get-version --display none
```

Output:

```text
1.2.3
```

#### Important Notes

- The `--display` option controls whether step commands are shown before execution
- This works independently of whether the operation has a `returns:` key (which controls stdout suppression)
- stderr is always displayed regardless of the `--display` setting
- If you don't specify `--display`, it defaults to `steps` mode

## list-operations

List all available public operations with their descriptions.

### Syntax

```bash
dyngle list-operations
```

### Output Format

The command outputs YAML-formatted list of operations:

```yaml
operations:
  build: Build the project for production
  test: Run the test suite
  deploy: Deploy to production
```

### Behavior

- Shows only **public** operations (not those with `access: private`)
- Includes the `description:` attribute if present
- Operations without descriptions show empty descriptions

See [Operations](operations.md#access) for information about public vs private operations.

## mcp

Start Dyngle as an MCP (Model Context Protocol) server, exposing operations as tools for AI assistants.

### Syntax

```bash
dyngle mcp
```

This starts a server using the `stdio` (standard input/output) transport, which is suitable for integration with Claude Desktop and other AI assistants.

### Configuration File

Specify a configuration file for the MCP server:

```bash
dyngle --config /path/to/.dyngle.yml mcp
```

See [MCP Server](mcp-server.md) for complete setup and usage information.

## Global Options

These options work with any command:

**`--config <path>`**

Specify a configuration file:

```bash
dyngle --config ./custom.yml run hello
```

## Next Steps

- [Learn about operations](operations.md)
- [Understand output modes](output-modes.md)
- [Set up the MCP server](mcp-server.md)
