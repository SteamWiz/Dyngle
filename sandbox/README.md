# Sandbox Examples

This directory contains focused examples demonstrating Dyngle features. Each example is self-contained and illustrates a specific concept.

## Core Examples

### hello-world.yml
The absolute minimal example - just a simple echo command.

**Usage:**
```bash
dyngle --config sandbox/hello-world.yml run hello
```

### templates.yml
Demonstrates template substitution with `{{variable}}` syntax.

**Usage:**
```bash
# Using stdin data
echo "name: Alice" | dyngle --config sandbox/templates.yml run greet

# Using inline values
dyngle --config sandbox/templates.yml run greet-with-values

# Nested properties
dyngle --config sandbox/templates.yml run nested-properties
```

### data-flow.yml
Shows data flow operators (`=>` for capture, `->` for input).

**Usage:**
```bash
dyngle --config sandbox/data-flow.yml run capture-output
dyngle --config sandbox/data-flow.yml run pipe-input
dyngle --config sandbox/data-flow.yml run pipeline
```

### expressions.yml
Demonstrates Python expressions for dynamic values.

**Usage:**
```bash
echo "name: Francis" | dyngle --config sandbox/expressions.yml run say-hello
```

## Intermediate Examples

### return-values.yml
Operations that return values to be used by other operations.

**Usage:**
```bash
dyngle --config sandbox/return-values.yml run use-return
dyngle --config sandbox/return-values.yml run process-and-return
```

### suboperations.yml
Comprehensive examples of sub-operations with isolation, send/receive, and data passing.

**Usage:**
```bash
dyngle --config sandbox/suboperations.yml run parent-isolated
dyngle --config sandbox/suboperations.yml run main-workflow
dyngle --config sandbox/suboperations.yml run pipeline
```

### access-control.yml
Demonstrates public vs private operations.

**Usage:**
```bash
# Can run public operation directly
dyngle --config sandbox/access-control.yml run public-operation

# Cannot run private operation directly (will fail)
dyngle --config sandbox/access-control.yml run private-helper
```

### imports.yml
Shows how to import operations from other files.

**Usage:**
```bash
dyngle --config sandbox/imports.yml run greet-from-import
```

### nested-data.yml
Accessing nested properties in data structures.

**Usage:**
```bash
dyngle --config sandbox/nested-data.yml run show-nested
dyngle --config sandbox/nested-data.yml run process-nested
```

## Advanced Examples

### interface-validation.yml
Input validation using the `accepts:` attribute with JSON Schema-like syntax.

**Usage:**
```bash
# Valid input
dyngle --config sandbox/interface-validation.yml --stream sandbox/greet-data.yml run greet

# Valid with nested data
dyngle --config sandbox/interface-validation.yml --stream sandbox/user-data.yml run create-user

# Invalid input (will show validation error)
echo "age: 16" | dyngle --config sandbox/interface-validation.yml run create-user
```

See the detailed usage instructions in the file's comments.

### recipe-analyzer.yml
A comprehensive real-world example demonstrating complex data processing with nested objects, arrays, and calculations.

See the file header for detailed usage instructions and sample data format.

## Supporting Data Files

- `greet-data.yml` - Sample data for interface-validation examples
- `user-data.yml` - Sample user data for validation examples
- `data.yml` - Generic sample data
- Other `.yml` files in sandbox/ may be data files for specific examples
