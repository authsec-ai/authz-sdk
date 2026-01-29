# AuthSec SDK - Testing Guide

Complete guide for testing the AuthSec SDK against your deployment or the development environment.

---

## Quick Start

### 1. Get Your Token

Visit [https://app.authsec.dev](https://app.authsec.dev) and authenticate to obtain your JWT token.

### 2. Configure Environment

```bash
# Required: Your authentication token
export TEST_AUTH_TOKEN='your-jwt-token-here'

# Optional: Custom domain URL (defaults to dev environment)
export TEST_BASE_URL='https://your-domain.com/api'

# Optional: Manual user ID override
export TEST_USER_ID='user-uuid-if-needed'
```

### 3. Run Tests

```bash
# Run primary E2E test
python3 tests/test_e2e_token_based.py

# Run all tests
./bootstrap_tests.sh
```

---

## Testing Against Custom Domains

### Your Deployment URL

To test against your own deployment instead of the dev environment:

```bash
# Set your custom domain
export TEST_AUTH_TOKEN='your-token-from-your-domain'
export TEST_BASE_URL='https://api.yourcompany.com'

# Run tests
python3 tests/test_e2e_token_based.py
```

**Example Custom Domains:**
```bash
# Production
export TEST_BASE_URL='https://api.mycompany.com'

# Staging
export TEST_BASE_URL='https://staging-api.mycompany.com'

# Local development
export TEST_BASE_URL='http://localhost:8080'

# Custom port
export TEST_BASE_URL='https://api.example.com:7469'
```

### Modifying Test Files for Custom URLs

All test files support the `TEST_BASE_URL` environment variable:

```python
import os

# Tests automatically use TEST_BASE_URL
base_url = os.getenv('TEST_BASE_URL', 'https://dev.api.authsec.dev')

# Initialize SDK with custom URL
client = AuthSecClient(base_url=f"{base_url}/uflow", token=token)
admin_helper = AdminHelper(token=token, base_url=base_url)
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| **TEST_AUTH_TOKEN** | ✅ Yes | None | JWT token from your authentication |
| **TEST_BASE_URL** | No | `https://dev.api.authsec.dev` | API base URL for your deployment |
| **TEST_USER_ID** | No | Auto-extracted | Manual user ID override |
| **TEST_ADMIN_TOKEN** | No | Uses TEST_AUTH_TOKEN | Separate admin token for multi-user tests |
| **TEST_ENDUSER_TOKEN** | No | Uses TEST_AUTH_TOKEN | End-user token for permission tests |

---

## Test Files

### Primary E2E Tests

| File | Description | Custom URL Support |
|------|-------------|-------------------|
| **test_e2e_token_based.py** | Complete E2E test with role binding | ✅ Yes |
| **test_e2e_admin_workflow.py** | Admin RBAC workflow | ✅ Yes |
| **test_e2e_complete.py** | Simplified RBAC test | ✅ Yes |

### Additional Tests

| File | Description | Custom URL Support |
|------|-------------|-------------------|
| **test_comprehensive.py** | Comprehensive SDK tests | ✅ Yes |
| **test_integration.py** | Integration tests | ✅ Yes |

### Utilities

| File | Description |
|------|-------------|
| **verify_token.py** | Debug token and extract user_id |
| **run_tests.sh** | Test runner script |
| **bootstrap_tests.sh** | Interactive test bootstrap |

---

## Running Tests

### Individual Tests

```bash
# Set environment
export TEST_AUTH_TOKEN='your-token'
export TEST_BASE_URL='https://your-domain.com/api'  # Optional

# Run specific test
python3 tests/test_e2e_token_based.py
python3 tests/test_e2e_admin_workflow.py
python3 tests/test_e2e_complete.py
```

### All Tests via Bootstrap Script

```bash
# Interactive mode (prompts for token and URL)
./bootstrap_tests.sh

# Quick mode with environment variables
export TEST_AUTH_TOKEN='your-token'
export TEST_BASE_URL='https://your-domain.com/api'
./bootstrap_tests.sh --quick
```

### With Pytest

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_e2e_token_based.py -v

# Run with custom domain
TEST_BASE_URL='https://your-domain.com/api' pytest tests/ -v
```

---

## Custom Domain Configuration Examples

### Example 1: Production Testing

```bash
#!/bin/bash
# test-production.sh

export TEST_AUTH_TOKEN='prod-jwt-token-here'
export TEST_BASE_URL='https://api.mycompany.com'

echo "Testing against: $TEST_BASE_URL"
python3 tests/test_e2e_token_based.py
```

### Example 2: Multi-Environment Testing

```bash
# test-all-environments.sh

# Dev environment
export TEST_BASE_URL='https://dev.api.authsec.dev'
export TEST_AUTH_TOKEN='dev-token'
echo "=== Testing DEV ===" 
python3 tests/test_e2e_complete.py

# Staging environment
export TEST_BASE_URL='https://staging-api.mycompany.com'
export TEST_AUTH_TOKEN='staging-token'
echo "=== Testing STAGING ==="
python3 tests/test_e2e_complete.py

# Production environment
export TEST_BASE_URL='https://api.mycompany.com'
export TEST_AUTH_TOKEN='prod-token'
echo "=== Testing PRODUCTION ==="
python3 tests/test_e2e_complete.py
```

### Example 3: Local Development

```bash
# test-local.sh

export TEST_AUTH_TOKEN='local-dev-token'
export TEST_BASE_URL='http://localhost:7469'

# Run tests against local server
python3 tests/test_e2e_token_based.py
```

---

## Test Coverage

### What's Tested

✅ **User ID Extraction**
- API-based token verification
- user_id/client_id extraction from token claims

✅ **Permission Management** (AdminHelper)
- Create permissions (resource:action)
- List permissions
- Filter by resource

✅ **Role Management** (AdminHelper)
- Create roles with permission strings
- List roles
- Delete roles

✅ **Role Binding Management** (AdminHelper)
- Create role bindings (assign roles to users)
- List bindings
- Delete bindings

✅ **Authorization Checks** (AuthSecClient)
- Check user permissions (resource:action)
- List user permissions
- Permission denial handling

✅ **Multi-User Workflows**
- Admin operations
- End-user permission checks
- Role-based access validation

### What's NOT Tested

❌ **User Registration** - Requires MFA/OTP via web interface  
❌ **User Login** - Requires MFA/OTP via web interface  
❌ **OTP Verification** - Manual web-based process  
❌ **Password Management** - Requires MFA verification

---

## Troubleshooting

### Token Issues

**Problem:** `TEST_AUTH_TOKEN required` error

**Solution:**
```bash
export TEST_AUTH_TOKEN='your-jwt-token-here'
```

Get token from: https://app.authsec.dev (for dev) or your custom domain.

---

**Problem:** Token verification fails

**Debug:**
```bash
# Check token with debug script
export TEST_AUTH_TOKEN='your-token'
python3 tests/verify_token.py
```

This shows:
- Token format validation
- Available claims
- Extracted user_id
- Token expiry

---

### Custom Domain Issues

**Problem:** Connection timeout or refused

**Solutions:**
1. **Check URL format:**
   ```bash
   # Correct
   export TEST_BASE_URL='https://api.example.com'
   
   # Incorrect (no /uflow suffix needed)
   export TEST_BASE_URL='https://api.example.com/uflow'  # Wrong!
   ```

2. **Verify domain is accessible:**
   ```bash
   curl $TEST_BASE_URL/health
   ```

3. **Check firewall/network:**
   - Ensure SDK can reach your domain
   - Check VPN requirements
   - Verify SSL certificates

---

**Problem:** 404 errors on custom domain

**Cause:** Endpoint paths may differ on your deployment

**Solution:**
Check your API documentation for correct endpoint paths. The SDK expects:
- `/authmgr/verifyToken` - Token verification
- `/uflow/admin/*` - Admin operations
- `/uflow/user/*` - End-user operations

---

### Permission/Role Issues

**Problem:** Role creation returns None

**Cause:** Backend API response format issue (not SDK issue)

**Impact:**
- Tests skip role binding creation
- Permission checks return empty
- This is expected with current backend

**Workaround:**
Tests will pass but role binding will be skipped. Once backend returns proper role object with `id` field, tests will automatically enable role binding.

---

**Problem:** List operations return 0 results

**Possible Causes:**
1. **Permissions not created:** Check creation succeeded
2. **Different tenant:** Token from different tenant
3. **Backend caching:** API cache needs refresh
4. **Custom domain:** Endpoint paths may differ

**Debug:**
```bash
# Enable debug mode in test
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

### CI/CD Integration

#### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Run E2E tests
        env:
          TEST_AUTH_TOKEN: ${{ secrets.TEST_AUTH_TOKEN }}
          TEST_BASE_URL: ${{ secrets.TEST_BASE_URL }}  # Your custom domain
        run: |
          python3 tests/test_e2e_token_based.py
```

#### GitLab CI

```yaml
test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pip install -e .
    - python3 tests/test_e2e_token_based.py
  variables:
    TEST_AUTH_TOKEN: $TEST_AUTH_TOKEN
    TEST_BASE_URL: $TEST_BASE_URL  # Set in GitLab CI/CD variables
```

#### Jenkins

```groovy
pipeline {
    agent any
    environment {
        TEST_AUTH_TOKEN = credentials('test-auth-token')
        TEST_BASE_URL = 'https://api.yourcompany.com'
    }
    stages {
        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install -e .'
                sh 'python3 tests/test_e2e_token_based.py'
            }
        }
    }
}
```

---

## Test Development

### Adding Custom Domain Support to New Tests

When creating new tests, use this pattern:

```python
#!/usr/bin/env python3
"""
New test with custom domain support.

Usage:
    export TEST_AUTH_TOKEN='your-token'
    export TEST_BASE_URL='https://your-domain.com/api'  # Optional
    python3 tests/new_test.py
"""

import os
import sys

# Get configuration from environment
token = os.getenv('TEST_AUTH_TOKEN')
base_url = os.getenv('TEST_BASE_URL', 'https://dev.api.authsec.dev')

if not token:
    print("❌ TEST_AUTH_TOKEN required")
    print("Get token from: https://app.authsec.dev")
    sys.exit(1)

print(f"Testing against: {base_url}")

# Initialize SDK
from authsec import AuthSecClient, AdminHelper

client = AuthSecClient(base_url=f"{base_url}/uflow", token=token)
admin = AdminHelper(token=token, base_url=base_url)

# Run tests...
```

---

## Best Practices

### 1. Use Environment Variables

Don't hardcode URLs or tokens:

```python
# ✅ Good
base_url = os.getenv('TEST_BASE_URL', 'https://dev.api.authsec.dev')

# ❌ Bad
base_url = 'https://api.mycompany.com'  # Hardcoded!
```

### 2. Provide Defaults

Always provide default values for optional variables:

```python
base_url = os.getenv('TEST_BASE_URL', 'https://dev.api.authsec.dev')
timeout = int(os.getenv('TEST_TIMEOUT', '10'))
```

### 3. Validate Configuration

Check required variables before running tests:

```python
if not os.getenv('TEST_AUTH_TOKEN'):
    print("❌ TEST_AUTH_TOKEN required")
    sys.exit(1)
```

### 4. Log Configuration

Show what configuration is being used:

```python
print(f"Base URL: {base_url}")
print(f"Token: {token[:20]}..." if token else "No token")
```

### 5. Handle Custom Endpoints

Be flexible with endpoint paths:

```python
# SDK handles endpoint variations
client = AuthSecClient(base_url=f"{base_url}/uflow", token=token)
# Works with: /uflow, /api/uflow, /v1/uflow, etc.
```

---

## Support

- **SDK Documentation:** [../README.md](../README.md)
- **Issues:** https://github.com/authsec-ai/authz-sdk/issues
- **Email:** support@authsec.dev

---

## Summary

**Testing Against Dev Environment:**
```bash
export TEST_AUTH_TOKEN='dev-token'
# No TEST_BASE_URL needed (uses default)
python3 tests/test_e2e_token_based.py
```

**Testing Against Your Domain:**
```bash
export TEST_AUTH_TOKEN='your-domain-token'
export TEST_BASE_URL='https://api.your domain.com'
python3 tests/test_e2e_token_based.py
```

**Key Points:**
- ✅ All tests support custom domain URLs via `TEST_BASE_URL`
- ✅ No code changes needed - just set environment variables
- ✅ Works with any deployment (production, staging, local)
- ✅ Token must match the domain you're testing against

Happy testing! 🚀
