#!/bin/bash
# Test script for sandbox examples
# Run from the project root: bash sandbox/test-examples.sh

set -e  # Exit on error

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "Testing Dyngle Sandbox Examples"
echo "========================================"
echo

# Helper function
test_operation() {
    local description="$1"
    local command="$2"
    echo -e "${BLUE}Testing: ${description}${NC}"
    echo "Command: ${command}"
    eval "${command}"
    echo -e "${GREEN}✓ Success${NC}"
    echo
}

# Core Examples
echo "=== Core Examples ==="
echo

test_operation "hello-world.yml - basic hello" \
    "python -m dyngle --config sandbox/hello-world.yml run hello"

test_operation "templates.yml - greet with stdin data" \
    "echo 'name: Alice' | python -m dyngle --config sandbox/templates.yml run greet"

test_operation "templates.yml - greet with inline constants" \
    "python -m dyngle --config sandbox/templates.yml run greet-with-constants"

test_operation "templates.yml - nested properties" \
    "python -m dyngle --config sandbox/templates.yml run nested-properties"

test_operation "data-flow.yml - capture output" \
    "python -m dyngle --config sandbox/data-flow.yml run capture-output"

test_operation "data-flow.yml - pipe input" \
    "python -m dyngle --config sandbox/data-flow.yml run pipe-input"

test_operation "data-flow.yml - pipeline" \
    "python -m dyngle --config sandbox/data-flow.yml run pipeline"

test_operation "expressions.yml - say-hello with stdin" \
    "echo 'name: Francis' | python -m dyngle --config sandbox/expressions.yml run say-hello"

# Intermediate Examples
echo "=== Intermediate Examples ==="
echo

test_operation "return-values.yml - use-return" \
    "python -m dyngle --config sandbox/return-values.yml run use-return"

test_operation "return-values.yml - process-and-return" \
    "python -m dyngle --config sandbox/return-values.yml run process-and-return"

test_operation "suboperations.yml - without-local" \
    "python -m dyngle --config sandbox/suboperations.yml run without-local"

test_operation "suboperations.yml - parent-isolated" \
    "python -m dyngle --config sandbox/suboperations.yml run parent-isolated"

test_operation "suboperations.yml - main-workflow" \
    "python -m dyngle --config sandbox/suboperations.yml run main-workflow"

test_operation "suboperations.yml - call-standalone" \
    "python -m dyngle --config sandbox/suboperations.yml run call-standalone"

test_operation "suboperations.yml - pipeline" \
    "python -m dyngle --config sandbox/suboperations.yml run pipeline"

test_operation "access-control.yml - public-operation" \
    "python -m dyngle --config sandbox/access-control.yml run public-operation"

test_operation "imports.yml - greet-from-import" \
    "python -m dyngle --config sandbox/imports.yml run greet-from-import"

test_operation "nested-data.yml - show-nested" \
    "python -m dyngle --config sandbox/nested-data.yml run show-nested"

test_operation "nested-data.yml - process-nested" \
    "python -m dyngle --config sandbox/nested-data.yml run process-nested"

# Advanced Examples
echo "=== Advanced Examples ==="
echo

test_operation "interface-validation.yml - greet with valid data" \
    "python -m dyngle --config sandbox/interface-validation.yml --stream sandbox/greet-data.yml run greet"

test_operation "interface-validation.yml - create-user with valid data" \
    "python -m dyngle --config sandbox/interface-validation.yml --stream sandbox/user-data.yml run create-user"

test_operation "interface-validation.yml - deploy" \
    "python -m dyngle --config sandbox/interface-validation.yml run deploy"

# Test that private operation fails
echo -e "${BLUE}Testing: access-control.yml - private-helper should fail${NC}"
echo "Command: python -m dyngle --config sandbox/access-control.yml run private-helper"
if python -m dyngle --config sandbox/access-control.yml run private-helper 2>/dev/null; then
    echo -e "${RED}✗ Failed: Private operation should not be accessible${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Success: Private operation correctly blocked${NC}"
fi
echo

# Test that invalid data fails validation
echo -e "${BLUE}Testing: interface-validation.yml - validation should fail for invalid data${NC}"
echo "Command: echo 'age: 16' | python -m dyngle --config sandbox/interface-validation.yml run create-user"
if echo "username: bob\nemail: bob@example.com\nage: 16" | python -m dyngle --config sandbox/interface-validation.yml run create-user 2>/dev/null; then
    echo -e "${RED}✗ Failed: Invalid data should have been rejected${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Success: Validation correctly rejected invalid data${NC}"
fi
echo

echo "========================================"
echo -e "${GREEN}All sandbox examples work as expected${NC}"
echo "========================================"
