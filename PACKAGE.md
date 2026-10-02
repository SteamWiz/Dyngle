# Dyngle

⚠️ DISCLAIMER: This is a hobby/personal project. Not a commercial product. Not for production use.

# Run lightweight local workflows

An experimental, lightweight, easily configurable workflow engine for automating development, operations, data processing, and content management tasks.

## Documentation

Complete documentation is available at **https://dyngle.steamwiz.io**

Key topics:

- **[Overview](https://dyngle.steamwiz.io/overview.html)** - Introduction and key features
- **[Quick Start](https://dyngle.steamwiz.io/quick-start.html)** - Get started with your first operation
- **[Operations](https://dyngle.steamwiz.io/operations.html)** - Define and run operations
- **[Command Steps](https://dyngle.steamwiz.io/command-steps.html)** - Data flow operators and command execution
- **[Operation Context](https://dyngle.steamwiz.io/operation-context.html)** - Templates and variable substitution
- **[Constants and Expressions](https://dyngle.steamwiz.io/constants-and-expressions.html)** - Python expressions and constants
- **[Sub-operations](https://dyngle.steamwiz.io/sub-operations.html)** - Compose operations from other operations
- **[Output Modes](https://dyngle.steamwiz.io/output-modes.html)** - Control operation output and return values
- **[MCP Server](https://dyngle.steamwiz.io/mcp-server.html)** - Expose operations as AI assistant tools
- **[Configuration](https://dyngle.steamwiz.io/configuration.html)** - Configuration files and imports
- **[CLI Commands](https://dyngle.steamwiz.io/cli-commands.html)** - Command reference

## Quick Example

Install:

```bash
pipx install dyngle
```

Create `.dyngle.yml`:

```yaml
dyngle:
  operations:
    hello:
      - echo "Hello world"
```

Run:

```bash
dyngle run hello
```

## Source Code

- **Repository:** https://github.com/SteamWiz/Dyngle
- **Issues:** https://github.com/SteamWiz/Dyngle/issues

## Contributing

For contributors and developers, see the [README.md](https://github.com/SteamWiz/Dyngle/blob/main/README.md) in the repository for development setup and guidelines.
