# Quick Start

Get up and running with Dyngle in minutes.

## Installation

Dyngle requires Python 3.13 or later.

On MacOS, try:

```bash
brew install pipx
```

Then:

```bash
pipx install dyngle
```

On Debian with Python already installed, try:

```bash
python3.13 -m pip install pipx
pipx install dyngle
```

In containers:

```bash
pip install dyngle
```

After installation, verify that Dyngle is working:

```bash
dyngle --help
```

You should see the command-line help output.

## Getting Started

Create a file called `.dyngle.yml` in your current directory:

```yaml
dyngle:
  operations:
    hello:
      - echo "Hello world"
```

Run the operation:

```bash
dyngle run hello
```

You should see:

```text
Hello world
```

## Referencing CLI arguments

Operations can reference arguments passed in to the `run` command.  Update your `.dyngle.yml`:

```yaml
dyngle:
  operations:
    hello:
      - echo "Hello {{runtime.args.0}}!"
```

Run the operation:

```bash
dyngle run hello 'Ada'
```

You should see:

```text
Hello Ada!
```

## Referencing structured data

Command line arguments provide some convenience, but many operations require a more complete data structure. In its simplest form, input data handling can be tried by piping YAML text to the `run` command.

```yaml
dyngle:
  operations:
    hello:
      - echo "Hello {{name}}!"
```

Run the operation:

```bash
echo "name: Katherine Johnson" | dyngle run hello
```

Output:

```text
Hello Katherine Johnson!
```

## Specifying an input data schema

With structured input data, it's possible to specify a schema which is validated when the operation runs. Use `accepts:` for that, and also move the commands a level down into a `steps:` entry.

```yaml
dyngle:
  operations:
    hello:
      accepts:
        full-name:
          required: true
      steps:
        - echo "Hello {{full-name}}!"
```

This will fail:

```bash
echo "name: Jane" | dyngle run hello
```

But of course this works:

```bash
echo "full-name: Jane Goodall" | dyngle run hello
```

## Performing logic with Python

Dyngle supports expressions that use Python, using a limited set of read-only operations.

The basic idea: Python for calculating, steps for doing things.

```yaml
dyngle: 
  operations:
    hello:
      accepts:
        first-name:
        last-name:
          required: true
      expressions:
        full-name: (first_name if first_name else 'Ms.') + ' ' + last_name
      steps:
        - echo "Hello {{full-name}}!"
```

```bash
echo "last-name: Curie" | dyngle run hello
```

```test
Hello Ms. Curie!
```

## Creating AI tools

Dyngle includes an MCP server to run its operations. To use it, we need to direct the output from the operation to a variable, and return the variable, so the operation becomes like a function.

```yaml
dyngle: 
  operations:
    hello:
      accepts:
        first-name:
        last-name:
      expressions:
        full-name: (first_name if first_name else 'Mx.') + ' ' + last_name
      steps:
        - echo "{{full-name}} says 'nice to meet you'." => greeting
      returns: greeting
```

To try it in Claude Desktop, edit or create `~/Library/Application Support/Claude/claude_desktop_config.json` (or equivalent in OS's other than MacOS).

```json
{"mcpServers": {"dyngle": {"command": "dyngle", "args": ["--config", "/absolute/path/to/your/project/.dyngle.mcp.yml", "mcp"]}}}
```

Then try a prompt:

```test
Say hello to Jennifer Doudna using the Dyngle tool.
```


## Read more

- [Learn about operations](operations.md)
- [Understand command steps](command-steps.md)
- [Explore operation context](operation-context.md)
- [Review best practices](best-practices.md)
