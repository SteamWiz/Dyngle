# Dyngle

⚠️ DISCLAIMER: This is a hobby/personal project. Not a commercial product. Not for production use.

## Run lightweight local workflows

An experimental, lightweight, easily configurable workflow engine for automating development, operations, data processing, and content management tasks.

## Technical Foundations

- **Configuration, task definition, and flow control in YAML** - Define your workflows in declarative YAML files
- **Operations as system commands** - Use familiar shell-like syntax for executing commands
- **Expressions and logic in pure Python** - Leverage Python for dynamic values and logic

## Key Features

- **Simple Operation Definition** - Define workflows as arrays of system commands ([learn more](operations.md))
- **Data Flow Operators** - Pipe data between steps with `=>` and `->` ([learn more](command-steps.md))
- **Conditional Steps** - Execute steps based on boolean conditions with `if/then/else` ([learn more](command-steps.md#conditional-steps))
- **Template Substitution** - Use `{{variable}}` or `$variable` syntax to inject data into commands ([learn more](operation-context.md))
- **Python Expressions** - Evaluate Python code for dynamic values ([learn more](constants-and-expressions.md))
- **Sub-operations** - Compose operations from other operations ([learn more](sub-operations.md))
- **MCP Server Support** - Expose operations as tools for AI assistants ([learn more](mcp-server.md))

## Use Cases

Dyngle is designed for:

- Development workflow automation (build, test, deploy)
- Operations tasks (server management, monitoring)
- Data processing pipelines
- Content management workflows
- AI assistant tool integration

## Read more

- [Quick Start](quick-start.md)
- [Learn about operations](operations.md)
- [Explore use cases](use-cases.md)
- [Review best practices](best-practices.md)

**❗️IMPORTANT: Read pages related to your requirements and _always read the best practices guide_ when developing Dyngle configuration!**