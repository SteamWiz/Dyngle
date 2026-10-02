# Use Cases

Real-world examples demonstrating how to use Dyngle for various tasks. These examples show practical patterns for building workflows, processing data, and integrating with AI assistants.

## Development Workflows

### Build Pipeline

Compose multiple build steps into a single operation:

```yaml
dyngle:
  operations:
    install-deps:
      access: private
      - npm install
    
    compile:
      access: private
      - npm run build
    
    test:
      access: private
      - npm test
    
    build:
      description: Full build pipeline
      steps:
        - sub: install-deps
        - sub: compile
        - sub: test
```

Users run `dyngle run build` to execute the complete pipeline, while individual steps remain private.

### Testing Module

Expose a test operation via MCP for AI assistants to run tests:

```yaml
dyngle:
  operations:
    run-tests:
      description: Run the test suite for a specific module
      accepts:
        module: { type: string }
      returns: test-results
      steps:
        - pytest {{module}} --json-report => results
        - results -> jq '.summary' => test-results
```

An AI assistant can run tests and understand the results to help debug issues.

### Continuous Integration

Build a complete CI/CD pipeline:

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

### Version Management

Query and manage versions across a project:

```yaml
dyngle:
  operations:
    get-version:
      description: Get version from package.json
      returns: version
      steps:
        - cat package.json -> jq -r '.version' => version
    
    tag-release:
      description: Tag a release with the current version
      steps:
        - sub: get-version
          receive: ver
        - git tag "v{{ver}}"
        - git push origin "v{{ver}}"
```

## Data Processing

### API Data Pipeline

Fetch and process data from an API:

```yaml
dyngle:
  operations:
    get-user-emails:
      description: Extract email addresses from user API
      returns: emails
      steps:
        - curl -s "https://api.example.com/users" => users
        - users -> jq -r '.[].email' => emails
```

### Log Analysis

Process log files to extract insights:

```yaml
dyngle:
  operations:
    analyze-logs:
      description: Count errors in today's logs
      returns: summary
      steps:
        - curl -s "https://logs.example.com/today" => logs
        - logs -> grep "ERROR" => errors
        - errors -> wc -l => error-count
        - echo "Found {{error-count}} errors" => summary
```

### Data Transformation

Transform JSON data through multiple stages:

```yaml
dyngle:
  operations:
    fetch-data:
      access: private
      returns: raw
      steps:
        - curl -s "https://api.example.com/data" => raw
    
    transform-data:
      access: private
      accepts:
        input: { type: string }
      returns: output
      steps:
        - input -> jq '.items | map({id, name})' => output
    
    process-all:
      description: Fetch and transform data
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

## Operations and Deployment

### Environment Deployment

Deploy to different environments with reusable setup:

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

### Multi-Environment Deployment

Deploy with environment-specific configuration:

```yaml
dyngle:
  operations:
    deploy:
      description: Deploy application to specified environment
      accepts:
        environment:
          type: string
        version:
          type: string
      steps:
        - sub: build
        - aws s3 sync ./dist s3://{{environment}}-bucket/{{version}}/
        - echo "Deployed v{{environment}} to {{environment}}"
    
    build:
      access: private
      - npm run build
```

### Service Health Check

Check service status and return structured information:

```yaml
dyngle:
  operations:
    check-service:
      description: Check the status of a specific application service
      accepts:
        service: { type: string }
      returns: status
      steps:
        - systemctl status {{service}} => output
        - echo "Service {{service}} is running" => status
```

Perfect for MCP integration - AI assistants can check service health.

## Secret Management

### Secure Credential Access

Protect operations that handle secrets:

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

The `get-api-token` operation is private so it can't be run directly or exposed via MCP, preventing accidental token exposure.

### Database Credentials

Safely manage database credentials:

```yaml
dyngle:
  operations:
    get-db-credentials:
      access: private
      returns: creds
      steps:
        - aws secretsmanager get-secret-value --secret-id db-creds => creds
    
    backup-database:
      description: Create database backup
      steps:
        - sub: get-db-credentials
          receive: creds
        - pg_dump -h {{creds.host}} -U {{creds.user}} > backup.sql
```

## AI Assistant Integration (MCP)

### Code Analysis

Expose operations that help AI assistants understand codebases:

```yaml
dyngle:
  operations:
    get-package-info:
      description: Get package information from package.json
      returns: info
      steps:
        - cat package.json => pkg
        - pkg -> jq '{name, version, description, dependencies}' => info
    
    get-dependencies:
      description: List all project dependencies
      returns: deps
      steps:
        - cat package.json -> jq '.dependencies | keys' => deps
```

### Project Information

Provide project context to AI assistants:

```yaml
dyngle:
  operations:
    project-summary:
      description: Get a summary of the project structure
      returns: summary
      expressions:
        summary:
          name: "get('pkg')['name']"
          version: "get('pkg')['version']"
          files: "get('file-count')"
      steps:
        - cat package.json => pkg
        - find . -type f | wc -l => file-count
```

### Development Environment Status

Help AI assistants understand the current development state:

```yaml
dyngle:
  operations:
    dev-status:
      description: Check development environment status
      returns: status
      expressions:
        status:
          git-branch: "get('branch')"
          uncommitted-changes: "get('changed-files')"
          node-version: "get('node-ver')"
      steps:
        - git branch --show-current => branch
        - git status --short | wc -l => changed-files
        - node --version => node-ver
```

## Content Management

### Document Processing

Process markdown or text files:

```yaml
dyngle:
  operations:
    count-words:
      description: Count words in a markdown file
      accepts:
        file: { type: string }
      returns: count
      steps:
        - cat {{file}} => content
        - content -> wc -w => count
    
    extract-headings:
      description: Extract headings from markdown
      accepts:
        file: { type: string }
      returns: headings
      steps:
        - cat {{file}} => content
        - content -> grep "^#" => headings
```

### Site Building

Build and deploy static sites:

```yaml
dyngle:
  operations:
    build-site:
      access: private
      - hugo build
    
    deploy-site:
      description: Build and deploy the site
      steps:
        - sub: build-site
        - aws s3 sync ./public s3://my-site-bucket/
        - aws cloudfront create-invalidation --distribution-id DIST123 --paths "/*"
```

## System Administration

### Backup Operations

Automated backup with composition:

```yaml
dyngle:
  operations:
    backup-files:
      access: private
      - tar -czf backup-$(date +%Y%m%d).tar.gz ./data
    
    upload-backup:
      access: private
      - aws s3 cp backup-*.tar.gz s3://backup-bucket/
    
    cleanup-old:
      access: private
      - find ./backup-*.tar.gz -mtime +7 -delete
    
    backup:
      description: Complete backup workflow
      steps:
        - sub: backup-files
        - sub: upload-backup
        - sub: cleanup-old
```

### Service Management

Manage application services:

```yaml
dyngle:
  operations:
    restart-app:
      description: Restart application services
      steps:
        - systemctl stop myapp
        - sleep 5
        - systemctl start myapp
        - systemctl status myapp
```

## Best Practices Demonstrated

### Composition Over Complexity

Break complex operations into smaller, focused operations:

**Good:**

```yaml
dyngle:
  operations:
    validate:
      access: private
      - python validate.py
    
    transform:
      access: private
      - python transform.py
    
    upload:
      access: private
      - aws s3 sync ./output s3://bucket/
    
    process:
      description: Complete processing workflow
      steps:
        - sub: validate
        - sub: transform
        - sub: upload
```

**Avoid:**

```yaml
dyngle:
  operations:
    process:
      - python validate.py
      - python transform.py
      - aws s3 sync ./output s3://bucket/
```

While the "avoid" version works, the composed version is more testable, maintainable, and allows reuse of individual steps.

### Clear Interfaces

Define explicit interfaces for operations:

```yaml
dyngle:
  operations:
    deploy-service:
      description: Deploy a service to an environment
      accepts:
        service-name: { type: string }
        environment: { type: string }
        version: { type: string }
      steps:
        - echo "Deploying {{service-name}} v{{version}} to {{environment}}"
```

This serves as documentation and provides validation.

### Return Meaningful Data

Operations exposed via MCP should return structured data:

```yaml
dyngle:
  operations:
    analyze-project:
      description: Analyze project health
      returns: analysis
      expressions:
        analysis:
          test-coverage: "get('coverage')"
          lint-errors: "get('errors')"
          build-status: "get('status')"
      steps:
        - pytest --cov --json-report => cov-report
        - cov-report -> jq '.coverage' => coverage
        - eslint . --format json => lint-report
        - lint-report -> jq '.[] | .errorCount' => errors
        - echo "healthy" => status
```

## Next Steps

- [Learn about operations](operations.md)
- [Explore sub-operations](sub-operations.md)
- [Set up MCP Server](mcp-server.md)
