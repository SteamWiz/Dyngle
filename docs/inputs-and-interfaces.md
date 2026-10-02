# Inputs and Interfaces

The `accepts:` attribute defines a schema for validating and defaulting operation inputs. This creates a clear contract for what data your operation expects.

## Interface Definition

Define an interface using the `accepts:` key in your operation:

```yaml
dyngle:
  operations:
    greet-user:
      accepts:
        name: { type: string }
        age: { type: integer }
      steps:
        - echo "Hello {{name}}, age {{age}}"
```

When inputs are provided (via stdin, `send:`, or MCP JSON), Dyngle validates them against this schema before executing the operation.

## Basic Syntax

The interface syntax is loosely based on JSON Schema but with adaptations tailored for Dyngle's use cases. While it shares some conventions (like type names), it has its own behavior for required fields, defaults, and type inference.

### Root Object

The interface always defines properties of a root object:

```yaml
accepts:
  field1: { type: string }
  field2: { type: integer }
```

This expects input like:

```yaml
field1: some text
field2: 42
```

## Type System

Supported types:

- **string** - Text values
- **integer** - Whole numbers (no decimals)
- **number** - Any numeric value (integers and floats)
- **boolean** - True or false values
- **array** - Lists of items
- **object** - Nested structures with properties

### Type Examples

```yaml
dyngle:
  operations:
    demo:
      accepts:
        text: { type: string }
        count: { type: integer }
        price: { type: number }
        enabled: { type: boolean }
        tags: 
          type: array
          items: { type: string }
        config:
          type: object
          properties:
            host: { type: string }
            port: { type: integer }
```

## Type Inference

Types can be inferred automatically based on other attributes:

```yaml
accepts:
  name: {}  # Defaults to string
  message:  # Also defaults to string (YAML null value)
  user:
    properties:
      email: { type: string }  # Inferred as object from properties
  tags:
    items: { type: string }  # Inferred as array from items
```

**Simplified syntax:** You can omit the field value entirely (YAML null) or use an empty dict `{}` for string fields with blank defaults. These are equivalent:

```yaml
accepts:
  name:  # YAML null - string with blank default
  title: {}  # Empty dict - string with blank default
  email: { type: string }  # Explicit string type
```

All three patterns above create optional string fields with blank string defaults.

**Precedence for type inference:**

1. Explicit `type:` if declared
2. `object` if `properties:` is present
3. `array` if `items:` is present
4. Otherwise `string`

## Required Fields and Defaults

Field requirements vary by type:

- **String fields** without explicit `required` or `default` get a blank string `""` as the default (making them optional)
- **Other types** are required by default unless marked `required: false` or given a `default`

### Examples

```yaml
accepts:
  name: {}  # String type, gets blank default "" if omitted
  nickname: { type: string, required: false }  # Also optional, no default
  age: { type: integer }  # Required (non-string type)
  email: { type: string, required: true }  # Explicitly required
```

### Default Values

Provide explicit default values for optional fields:

```yaml
accepts:
  name: { type: string }  # Gets blank string if omitted
  country:
    type: string
    default: "US"  # Gets "US" if omitted
  port:
    type: integer
    default: 8080  # Gets 8080 if omitted
```

Having an explicit `default` makes the field optional automatically.

## Nested Objects

Define nested structures with `properties:`. The `object` type is automatically inferred from the presence of `properties:`, so you don't need to declare it explicitly:

```yaml
dyngle:
  operations:
    process-order:
      accepts:
        customer:
          properties:  # object type inferred
            name:  # string type inferred (YAML null)
            email:
        shipping:
          properties:  # object type inferred
            address:
            city:
            zip:
      steps:
        - echo "Processing order for {{customer.name}}"
        - echo "Shipping to {{shipping.city}}"
```

You can nest objects arbitrarily deep:

```yaml
accepts:
  order:
    properties:
      shipping:
        properties:
          address:
            properties:  # deeply nested object
              street:
              city:
              state:
```

## Arrays

Define array types with `items`:

```yaml
accepts:
  tags:
    type: array
    items: { type: string }
  scores:
    items: { type: integer }  # type: array inferred from items
```

### Arrays of Objects

Combine arrays with nested objects. The `array` type is inferred from `items:`, and the `object` type for each item is inferred from `properties:`:

```yaml
accepts:
  items:
    items:  # array type inferred
      properties:  # object type inferred for each item
        product:  # string type inferred
        quantity: { type: integer }
        price: { type: number }
```

## Validation Process

When an operation with `accepts:` is invoked:

1. **Input is received** (from stdin, `send:`, or MCP JSON)
2. **Schema validation** - Input structure is checked against the interface
3. **Type validation** - Values are checked for correct types
4. **Defaults applied** - Missing optional fields get their defaults
5. **Required fields checked** - Missing required fields cause an error
6. **Execution proceeds** - Validated input becomes available in the operation context

### Validation Success

```bash
echo "name: Alice\nage: 30" | dyngle run greet-user
# Output: Hello Alice, age 30
```

### Validation Failure

```bash
echo "age: 30" | dyngle run greet-user
# Error: Input validation failed for operation 'greet-user': 
# Field 'name' is required at root
```

### Extra Fields

Extra fields are allowed by default:

```bash
echo "name: Bob\nage: 25\ncity: Seattle" | dyngle run greet-user  
# Output: Hello Bob, age 25 (city is ignored)
```

## Complete Example

This example demonstrates all the key features including type inference, nested objects, arrays, defaults, and required fields:

```yaml
dyngle:
  operations:
    create-user:
      description: Create a new user account
      accepts:
        username:  # string with blank default (optional)
        email: { type: string, required: true }  # explicitly required
        age: { type: integer }  # required (non-string type)
        role: { default: "user" }  # string with custom default
        preferences:
          properties:  # object type inferred
            theme: { default: "light" }
            notifications: { type: boolean, default: true }
        tags:
          items:  # array type inferred
            type: string
          default: []
      returns: result
      steps:
        - echo "Creating user {{username}} ({{email}})"
        - echo "Role: {{role}}, Age: {{age}}"
        - echo "Theme: {{preferences.theme}}"
        - echo "User created successfully" => result
```

## Using Interfaces with Sub-operations

When using `send:` to pass data to sub-operations, the data is validated against the child operation's `accepts:` schema. This example shows nested objects being passed via `send:`:

```yaml
dyngle:
  operations:
    process-user:
      accepts:
        user:
          properties:  # object type inferred
            name:  # string type inferred
            email:
            age: { type: integer }
      steps:
        - echo "Processing {{user.name}}, age {{user.age}}"
    
    main:
      constants:
        user-data:
          user:
            name: Alice
            email: alice@example.com
            age: 30
      steps:
        - sub: process-user
          send: user-data  # Nested structure validated against accepts schema
```

If validation fails, the parent operation stops with an error.

## Using Interfaces with MCP

When operations are exposed via the MCP server, the `accepts:` schema determines the tool's input parameters:

**With accepts:**

```yaml
dyngle:
  operations:
    get-weather:
      description: Get current weather for a city
      accepts:
        city: { type: string }
        units:
          type: string
          default: "metric"
      returns: weather-info
      steps:
        - curl -s "https://api.example.com/weather?city={{city}}&units={{units}}" => weather-info
```

The MCP tool will have `city` and `units` as input parameters, with validation and defaults applied automatically.

**Without accepts:**

```yaml
dyngle:
  operations:
    run-backup:
      description: Run the nightly backup process
      returns: result
      steps:
        - /usr/local/bin/backup.sh => result
```

The MCP tool will have no input parameters.

See [MCP Server](mcp-server.md) for more details.

## Best Practices

### Use accepts for Public Operations

Operations exposed via MCP or called as sub-operations should define their interfaces. Use the simplified syntax for cleaner definitions:

```yaml
dyngle:
  operations:
    deploy-service:
      description: Deploy a service to an environment
      accepts:
        service-name:  # string type inferred
        environment:
        version:
      steps:
        - echo "Deploying {{service-name}} v{{version}} to {{environment}}"
```

### Provide Sensible Defaults

Use defaults for optional parameters to make operations easier to use:

```yaml
accepts:
  environment:
    type: string
    default: "development"
  verbose:
    type: boolean
    default: false
```

### Document with Field Descriptions

Use `description:` on individual fields to document their purpose. Field descriptions are passed through to MCP tools and other dynamic contexts:

```yaml
dyngle:
  operations:
    process-data:
      description: Process data file with optional validation
      accepts:
        filename:
          type: string
          description: Path to the data file to process
        format:
          type: string
          default: "json"
          description: Data format (json or csv)
        validate:
          type: boolean
          default: true
          description: Whether to validate data before processing
```

Field descriptions are especially important for operations exposed via MCP or used as sub-operations, as they help users understand what each parameter does.

## Next Steps

- [Learn about constants and expressions](constants-and-expressions.md)
- [Understand sub-operations](sub-operations.md)
- [Explore MCP Server integration](mcp-server.md)
