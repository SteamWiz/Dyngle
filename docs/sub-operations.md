# Sub-operations

Operations can call other operations as steps, enabling composability and code reuse. Sub-operation steps are the second type of operation step (alongside command steps).

## Basic Usage

Use the `sub:` key to call another operation:

```yaml
dyngle:
  operations:
    greet:
      - echo "Hello!"
    
    greet-twice:
      steps:
        - sub: greet
        - sub: greet
```

## Passing Data with send:

To pass data to a sub-operation, use the `send:` attribute:

```yaml
dyngle:
  operations:
    greet-person:
      steps:
        - echo "Hello, {{name}}!"
    
    main:
      constants:
        user:
          name: Alice
      steps:
        - sub: greet-person
          send: user  # Pass data to child
```

The data's keys and values become inputs in the sub-operation's context.

### Template Structures in send:

The `send:` attribute can accept template structures, allowing you to construct data inline:

```yaml
dyngle:
  operations:
    deploy:
      steps:
        - echo "Deploying {{username}} to {{environment}}"
    
    main:
      constants:
        user: alice
        env: production
      steps:
        - sub: deploy
          send:
            username: $user
            environment: $env
            timestamp: "{{runtime.timestamp}}"
```

You can use either `$variable` or `"{{variable}}"` syntax for template references.

This is equivalent to defining a constant and passing it, but more concise:

```yaml
# Equivalent to:
main:
  constants:
    user: alice
    env: production
    deploy-data:
      username: "{{user}}"
      environment: "{{env}}"
      timestamp: "{{runtime.timestamp}}"
  steps:
    - sub: deploy
      send: deploy-data
```

Template structures support:
- **Nested properties**: Reference values like `{{config.host}}`
- **Non-string constants**: Include integers, booleans, and floats directly
- **Nested structures**: Create complex nested dictionaries

Example with nested structure:

```yaml
dyngle:
  operations:
    configure:
      steps:
        - echo "Server: {{server.host}}:{{server.port}}"
    
    main:
      constants:
        host: example.com
        port: 8080
      steps:
        - sub: configure
          send:
            server:
              host: "{{host}}"
              port: "{{port}}"
            enabled: true
```

## Capturing Results with receive:

When a sub-operation has a `returns:` key, capture its value with `receive:`:

```yaml
dyngle:
  operations:
    get-version:
      returns: ver
      steps:
        - cat package.json -> jq -r '.version' => ver
    
    tag-release:
      steps:
        - sub: get-version
          receive: version  # Capture return value
        - git tag "v{{version}}"
```

If the sub-operation has no `returns:` key, `receive:` stores `None`.

## send: and receive: Together

Combine both to create function-like operations:

```yaml
dyngle:
  operations:
    double:
      accepts:
        num: { type: integer }
      returns: result
      expressions:
        result: "num * 2"
      steps:
        - echo "Doubling {{num}}"
    
    main:
      constants:
        params:
          num: 5
      steps:
        - sub: double
          send: params      # Send input
          receive: doubled  # Capture output
        - echo "Result: {{doubled}}"
```

## Similarity to Command Steps

Note the similarity between the `send:` and `receive:` attributes in sub-operation steps and the `->` (send) and `=>` (receive) operators in command steps:

**Command step:**
```yaml
- input-data -> command => output-data
```

**Sub-operation step:**
```yaml
- sub: operation-name
  send: input-data
  receive: output-data
```

Both follow the same pattern: data flows in via send/`->`, gets processed, and flows out via receive/`=>`.

## Input Validation with accepts:

Define what data an operation accepts using `accepts:`:

```yaml
dyngle:
  operations:
    process-user:
      accepts:
        user-id: { type: string }
        email: { type: string }
      steps:
        - echo "Processing {{user-id}}: {{email}}"
    
    main:
      constants:
        user-data:
          user-id: "12345"
          email: user@example.com
      steps:
        - sub: process-user
          send: user-data  # Validated before execution
```

If the sent data doesn't match the `accepts:` schema, the operation fails with a clear error message. See [Inputs and interfaces](inputs-and-interfaces.md) for complete details.

## Operation Context Scope

Sub-operations are isolated by default - they do not automatically see the parent operation's context. This isolation makes operations **predictable** and **testable** - they behave like pure functions.

### Isolation by Default

```yaml
dyngle:
  operations:
    child:
      steps:
        - echo "{{parent-val}}"  # ERROR: parent-val not found
    
    parent:
      steps:
        - echo "secret" => parent-val
        - sub: child  # child cannot see parent-val
```

To share data between parent and child, use explicit `send:` and `receive:` attributes.

### Constants and Expressions

Both declared constants (`constants:`/`expressions:`) and variables (`=>` assignments) are operation-local due to isolation:

**Constants and expressions** - Each operation sees only its own declarations plus globals:

```yaml
dyngle:
  constants:
    global-val: Available to all
  
  operations:
    child:
      constants:
        local-val: Child only
      steps:
        - echo "{{global-val}}"  # OK - global
        - echo "{{local-val}}"   # OK - local to child
    
    parent:
      constants:
        parent-val: Parent only
      steps:
        - echo "{{global-val}}"   # OK - global
        - echo "{{parent-val}}"   # OK - local to parent
        - sub: child
        # child cannot see parent-val
```

**Variables** - Each operation maintains its own variables; `=>` assignments don't cross boundaries:

```yaml
dyngle:
  operations:
    child:
      steps:
        - echo "child-result" => data
        - echo "Child data: {{data}}"
    
    parent:
      steps:
        - echo "parent-result" => data
        - echo "Parent data: {{data}}"  # "parent-result"
        - sub: child
        - echo "After child: {{data}}"  # Still "parent-result" (child's data isolated)
```

### Complete Isolation Example

```yaml
dyngle:
  constants:
    declared-val: global
  
  operations:
    child:
      constants:
        declared-val: child-local
      steps:
        - echo "{{declared-val}}"  # "child-local" (own declaration)
        - echo "result" => live-data
    
    parent:
      steps:
        - echo "{{declared-val}}"  # "global" (no local override)
        - echo "parent" => live-data
        - sub: child
        - echo "{{declared-val}}"  # Still "global"
        - echo "{{live-data}}"     # Still "parent" (child's data isolated)
```

### Data Sharing

Use `send:` and `receive:` for explicit parent-child data flow:

```yaml
dyngle:
  operations:
    child:
      returns: result
      steps:
        - echo "Processing {{input-value}}"
        - echo "done" => result
    
    parent:
      constants:
        data:
          input-value: hello
      steps:
        - sub: child
          send: data       # Explicitly share data
          receive: output  # Explicitly capture result
        - echo "Got: {{output}}"
```

## Use Cases

### Build Pipeline

```yaml
dyngle:
  operations:
    install-deps:
      - npm install
    
    compile:
      - npm run build
    
    test:
      - npm test
    
    build:
      description: Full build pipeline
      steps:
        - sub: install-deps
        - sub: compile
        - sub: test
```

### Reusable Components with Private Operations

```yaml
dyngle:
  operations:
    setup-env:
      access: private
      steps:
        - echo "Setting up environment..."
        - export NODE_ENV=production
    
    deploy-frontend:
      description: Deploy frontend application
      steps:
        - sub: setup-env
        - npm run deploy:frontend
    
    deploy-backend:
      description: Deploy backend services
      steps:
        - sub: setup-env
        - npm run deploy:backend
```

### Data Processing Pipeline

```yaml
dyngle:
  operations:
    fetch-data:
      returns: raw
      steps:
        - curl -s "https://api.example.com/data" => raw
    
    transform-data:
      accepts:
        input: { type: string }
      returns: output
      steps:
        - input -> jq '.items' => output
    
    process-all:
      returns: final
      steps:
        - sub: fetch-data
          receive: data
        - sub: transform-data
          send: payload
          receive: final
      constants:
        payload:
          input: "{{data}}"
```

### Helper Operations for Secrets

Prevent accidental exposure of operations that handle secrets:

```yaml
dyngle:
  operations:
    get-api-token:
      access: private
      returns: token
      steps:
        - aws secretsmanager get-secret-value --secret-id api-token => secret
        - secret -> jq -r '.SecretString' => token
    
    call-api:
      description: Make authenticated API call
      steps:
        - sub: get-api-token
          receive: token
        - curl -H "Authorization: Bearer {{token}}" https://api.example.com/data
```

This prevents running `dyngle run get-api-token` accidentally or exposing it through the MCP server.

### Multi-Step Workflows with Composition

Build complex workflows from smaller private operations:

```yaml
dyngle:
  operations:
    install-dependencies:
      access: private
      - npm install
    
    run-tests:
      access: private
      - npm test
    
    build-artifacts:
      access: private
      - npm run build
    
    upload-artifacts:
      access: private
      - aws s3 sync ./dist s3://my-bucket/
    
    ci-pipeline:
      description: Run full CI/CD pipeline
      steps:
        - sub: install-dependencies
        - sub: run-tests
        - sub: build-artifacts
        - sub: upload-artifacts
```

Users only see and can run `ci-pipeline`, not the internal helpers.

## Best Practices

### Use accepts: for Clear Contracts

Define what data your operations need:

```yaml
dyngle:
  operations:
    deploy-service:
      accepts:
        service-name: { type: string }
        version: { type: string }
        environment: { type: string }
      steps:
        - echo "Deploying {{service-name}} v{{version}} to {{environment}}"
```

This serves as self-documentation and catches errors early.

### Explicit is Better Than Implicit

Always use `send:` and `receive:` for data flow:

**Good:**

```yaml
dyngle:
  operations:
    get-version:
      returns: version
      steps:
        - cat package.json -> jq -r '.version' => version
    
    tag-release:
      steps:
        - sub: get-version
          receive: ver
        - git tag "v{{ver}}"
```

**Avoid (this won't work due to isolation):**

```yaml
dyngle:
  operations:
    get-version:
      steps:
        - cat package.json -> jq -r '.version' => version
    
    tag-release:
      steps:
        - sub: get-version
        - git tag "v{{version}}"  # ERROR: version not found
```

### Use Private Operations for Helpers

Mark helper operations as `private` to prevent direct execution:

```yaml
dyngle:
  operations:
    deploy:
      description: Deploy the application
      steps:
        - sub: validate
        - sub: build
        - sub: upload
    
    validate:
      access: private
      steps:
        - echo "Validating configuration..."
    
    build:
      access: private
      steps:
        - npm run build
    
    upload:
      access: private
      steps:
        - aws s3 sync ./dist s3://my-bucket/
```

### Make Public Operations User-Facing

Public operations should represent complete, user-facing actions, while private operations are focused, reusable components.

## Next Steps

- [Learn about output modes](output-modes.md)
- [Understand operation context scope](operation-context.md)
- [Explore use cases](use-cases.md)
