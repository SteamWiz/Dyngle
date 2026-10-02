# Configuration

Dyngle reads configuration from YAML files that define operations, expressions, constants, and other settings.

## Configuration File Location

Dyngle searches for configuration files in the following order (first match wins):

1. **Command line option**: `--config` parameter
2. **Environment variable**: `DYNGLE_CONFIG`
3. **Current directory**: `.dyngle.yml`
4. **Home directory**: `~/.dyngle.yml`

### Examples

Using a specific config file:

```bash
dyngle --config /path/to/config.yml run my-operation
```

Using an environment variable:

```bash
export DYNGLE_CONFIG=/path/to/config.yml
dyngle run my-operation
```

## Configuration Structure

A basic configuration file has this structure:

```yaml
dyngle:
  operations:
    # Your operations here
    
  expressions:
    # Global expressions (optional)
    
  constants:
    # Global constants (optional)
```

## Imports

Configuration files can import other configuration files, allowing you to organize your operations across multiple files and share common configurations.

### Basic Import

Import other configuration files using the `imports:` key:

```yaml
dyngle:
  imports:
    - ~/.dyngle.yml
    - ./common-operations.yml
  operations:
    # Operations defined here
```

### Import Behavior

- Imports are loaded in the order specified
- Later imports override earlier ones in case of name conflicts
- Operations and expressions in the main file override all imports
- **Imports are recursive** - imported files can import other files

### Use Cases

**User-level configuration:**

Create a `~/.dyngle.yml` with common operations, then import it in project-specific configs:

```yaml
# ~/.dyngle.yml
dyngle:
  operations:
    cleanup:
      - rm -rf .venv
      - rm -rf node_modules
```

```yaml
# project/.dyngle.yml
dyngle:
  imports:
    - ~/.dyngle.yml
  operations:
    build:
      - npm install
      - npm run build
```

**Shared team operations:**

```yaml
# team-shared.yml
dyngle:
  operations:
    deploy-staging:
      - sub: build
      - aws s3 sync ./dist s3://staging-bucket/

# developer's local config
dyngle:
  imports:
    - ./team-shared.yml
  operations:
    dev:
      - npm run dev
```

## Next Steps

- [Define operations](operations.md)
- [Learn about CLI commands](cli-commands.md)
- [Use expressions for dynamic values](constants-and-expressions.md)
