# Operation Lifecycle

Understanding how Dyngle executes operations helps you design effective workflows.

## Execution Steps

When you run an operation, Dyngle follows this lifecycle:

### 1. Load Configuration

Dyngle locates and loads the configuration file using a specific search order.

See [Configuration](configuration.md#configuration-file-location) for the complete search order and details.

### 2. Process Imports

If the configuration contains `imports:`, Dyngle loads the imported files recursively.

### 3. Load Inputs

If stdin is not a tty (e.g., data is piped in), Dyngle parses it as YAML and adds it to the operation context as inputs.

```bash
echo "name: Alice" | dyngle run greet
```

### 4. Find the Operation

Dyngle looks up the named operation in the configuration. If not found, it returns an error.

### 5. Check Access Control

For direct execution via `dyngle run`, Dyngle verifies the operation is public. Private operations can only be called as sub-operations.

### 6. Initialize Operation Context

Dyngle builds the initial operation context by merging (in order of precedence):

1. Global constants from `dyngle: constants:`
2. Global expressions from `dyngle: expressions:`
3. Operation-specific constants
4. Operation-specific expressions
5. Inputs from stdin

See [Operation context](operation-context.md#context-key-precedence) for details on precedence.

### 7. Execute Steps

For each step in the operation:

#### Template Rendering

Dyngle renders templates in the step, replacing `{{variable}}` syntax with values from the operation context.

#### Parse Step

Dyngle parses the step to identify:
- Send operator (`->`)
- Command and arguments (for command steps) or sub-operation reference (for sub-operation steps)
- Receive operator (`=>`)

#### Execute Step

**For command steps:**
- Dyngle runs the command using Python's `subprocess.run()`
- If there's a send operator, the value is passed to stdin
- stdout and stderr are captured
- The exit code is checked

**For sub-operation steps:**
- Dyngle executes the sub-operation with its own isolated context
- If there's a `send:` attribute, data is passed to the sub-operation as inputs
- The sub-operation's return value (if any) is captured

#### Update Operation Context

If there's a receive operator (`=>`) or `receive:` attribute, the captured value is stored in the operation context as a variable with the specified name.

### 8. Handle Return Value

If the operation has a `returns:` key:

1. Dyngle looks up the specified value in the operation context
2. For `dyngle run`, it formats and displays the value
3. For sub-operations, the value is made available to the parent via `receive:`
4. For MCP tools, the value is returned as `{"result": <value>}`

See [Output modes](output-modes.md) for details on how returns work in different contexts.

## Operation Context Evolution

The operation context changes throughout execution:

```yaml
dyngle:
  constants:
    base: Initial
  operations:
    example:
      constants:
        local: Added
      expressions:
        computed: "'Calculated'"
      steps:
        - echo "first" => step1    # Adds 'step1' variable to context
        - echo "second" => step2   # Adds 'step2' variable to context
```

Context evolution:

1. **Start**: `{base: "Initial"}`
2. **After init**: `{base: "Initial", local: "Added", computed: "Calculated"}`
3. **After step 1**: `{base: "Initial", local: "Added", computed: "Calculated", step1: "first"}`
4. **After step 2**: `{base: "Initial", local: "Added", computed: "Calculated", step1: "first", step2: "second"}`

## Sub-operation Context Isolation

When a step calls a sub-operation, each operation maintains its own isolated context. Data is shared explicitly through `send:` and `receive:` attributes.

See [Sub-operations](sub-operations.md#operation-context-scope) for detailed explanation of context isolation.

## Error Handling

### Command Failures

If a command returns a non-zero exit code:

1. Dyngle stops execution
2. stderr is displayed
3. The operation returns an error
4. For MCP tools, returns `{"error": "<message>"}`

### Template Errors

If a template references an undefined variable:

1. Dyngle raises an error
2. Execution stops
3. The error message identifies the missing variable

### Access Control Errors

If you try to run a private operation directly:

1. Dyngle checks the `access:` attribute
2. If private, returns an error immediately
3. Execution never starts

## Performance Considerations

### Command Execution

Each step spawns a new subprocess:
- Minimal overhead for simple commands
- Consider batching operations when possible

### Template Rendering

Templates are rendered for each step:
- Efficient for small datasets
- Large data structures are passed by reference in the context

### Data Flow

Data captured with `=>` is held in memory:
- Suitable for typical command output
- Be cautious with very large outputs (e.g., large files)

## Next Steps

- [Learn about operations](operations.md)
- [Understand operation context](operation-context.md)
- [Explore sub-operations](sub-operations.md)
