# Dyngle vision

A lightweight local workflow engine

## Description

### Use cases

- Common day-to-day shell operations, i.e. replace:
  - Makefile entries where we use `.PHONY`
  - Short local bash or python scripts
  - Functions and aliases in e.g. `.zshrc` files
- AI tools and MCP servers
- Avoids awkward bash syntax (example: `if [ -z ... ]`)
- Wrap common CLIs with specific use cases (including curl!)

### A dyngle operation is designed to be run either:

- In a login shell, where the user might interact
- In a background process, such as on a server or cron job, where stdin drives options

### Basic characteristics

- Expressions and operations are configured in YAML
- Operations take no arguments except for stdin, which is assumed to be YAML
- Operations return YAML to stdout (TODO)
- Expressions in Python; operations are a series of system commands
- Both expressions and operations are evaluated using a custom template substitution syntax

We walk a fine line, because we want to avoid the impression of intending to create an entirely new programming language. This is a meta-language, a wrapper around commands with a more pleasing (to me) syntax than Bash functions, Makefiles, or pure Python.

Dyngle itself is not a security layer, in that it doesn't protect against malicious configuration. But it is, in that a configuration can restrict the operations that a user can perform.

There are no "variables" per se other than the main data set. The steps in an operation are not able to set env vars.

We also have _commands_ which use Python (with a more extended set of capabilities) to form _very simple_ commands that get (essentially) added to the PATH.

### Random ideas

- Use case: Sync Busy tasks with assigned GitHub issues
- Idea: Separate tool for interactivity, which could use AI or not

### What it is NOT

- Network-aware or multi-user
- A queueing system or a stateful process engine - operations run to completion in memory
- Container-oriented (though it might run in containers nicely)
- A replacement for CI/CD (thought it might run nicely inside CI/CD)
- Fully Bash-compliant -- except for whitespace-separated arguments to system commands, it shares no syntax with Bash
- Fault-tolerant

## Examples

Some ideas about how Dyngle might work in the future.

### As we've used Make

A simple array of commands with whitespace-separated arguments. Each line _looks_ a little like a shell line, but is much more primitive in reality.

```yaml
operations:
  init:
    - rm -rf .venv
    - python3.11 -m venv .venv
    - .venv/bin/pip install --upgrade pip poetry
```

### As we've used small Bash functions

Here's a function which creates a GitHub pull request and starts working on it, using a specific convention for the branch name.

```bash
pr () {
	TITLE=$1
	BRANCH=$(date +%Y%m%d)-$2
	git checkout -b "$BRANCH"
	git commit --allow-empty -m "$TITLE"
	git push -u origin "$BRANCH"
	gh pr create --draft --title "$TITLE" --body ''
}
```

In Dyngle, it would work with input such as

```yaml
title: Build big pyramids in the desert
branch-name: build-big-pyramids
```

```yaml
expressions:
  # Note that strftime() doesn't work
  dated-branch-name: >-
    formatted(datetime.now()) + '-' + branch_name
operations:
  pr:
    - git checkout -b {{dated-branch-name}}
    - git commit --allow-empty -m "{{title}}"
    - git push -u origin {{dated-branch-name}}
    - gh pr create --draft --title "{{title}}" --body ''
```

But soon we plan to add sys.argv as a valid name in expressions!

```yaml
expressions:
  title: argv[1]
  branch-name: argv[2]
  dated-branch-name: >-
    formatted(datetime.now()) + '-' + branch_name
# ...
```


### A restricted write operation

Of course it's possible to write to a file using a shell.

```yaml
dyngle:
  operations:
    write:
      - sh -c "echo 'Hello again' > delete-me.z"
```

This could be used e.g. as a tool for an AI agent, where it's only allowed to write to a specific directory.
So we intend to build in a restricted "write" command.

```yaml
file: directory/file.txt
content: |
    I like snakes.
    Bears like me.
```

```yaml
dyngle:
  expressions:
    writer: >-
      Path(file).write_text(content)
  operations:
    write:
      - cat {{writer}}
```

This is problematic because it's mixing write operations into expressions, and will get weird if the expression is called multiple times. But at the moment it works.

We also had the idea of "primitives" like `assert` and `write` that would work as commands within dyngle itself.

Also we _really_ need expressions to cache output for the same data values. Or certain data values. Or something.

### Conditional

```yaml
dyngle:
  expressions:
    notebook-exists-not: "not Path('notebook.md')"
  operations:
    read-notes:
      - if: '{{notebook-exists-not}}'
        then:
          - touch notebook.md
          - git add notebook.md
          - git commit -am 'notebook'
          - git push
      - cat notebook.md
```

### Looping

```yaml
dyngle:
  operations:
    busy:
      - busy activate
      - loop: 
          - busy pick first
          - if: 'not output'
            then: unloop
          - zsh
```
