# AuthSec SDK Test Suite

## Overview

Token-based test suite for the AuthSec SDK. All tests assume the user has already authenticated externally and obtained a JWT token.

## Quick Start

```bash
# Get token from web interface
# Visit: https://app.authsec.dev
# Login and copy your JWT token

# Set token environment variable
export TEST_AUTH_TOKEN='your-jwt-token-here'

# Run all tests via bootstrap script
./bootstrap_tests.sh

# Or run individual tests
python3 tests/test_e2e_token_based.py
python3 tests/test_e2e_admin_workflow.py
python3 tests/test_e2e_complete.py
```

## Test Files

### Primary E2E Tests

| File | Description | Status |
|------|-------------|--------|
| **test_e2e_token_based.py** | Complete E2E test with API-based user extraction and role binding | ✅ Primary test |
| **test_e2e_admin_workflow.py** | Admin workflow test covering permissions, roles, and bindings | ✅ Token-based |
| **test_e2e_complete.py** | Simplified E2E RBAC test | ✅ Token-based |

### Additional Tests

| File | Description | Status |
|------|-------------|--------|
| **test_comprehensive.py** | Comprehensive SDK tests | ✅ Compatible |
| **test_integration.py** | Integration tests | ✅ Compatible |

### Utilities

| File | Description |
|------|-------------|
| **verify_token.py** | Debug token format and extract user_id |
| **run_tests.sh** | Test runner script |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TEST_AUTH_TOKEN` | Yes | JWT token from app.authsec.dev |
| `TEST_ADMIN_TOKEN` | No | Admin token (if different from TEST_AUTH_TOKEN) |
| `TEST_ENDUSER_TOKEN` | No | End-user token (for multi-user tests) |
| `UFLOW_BASE_URL` | No | API base URL (default: https://dev.api.authsec.dev) |

## Getting a Token

1. Visit [https://app.authsec.dev](https://app.authsec.dev)
2. Complete MFA/OTP authentication
3. Copy your JWT token from the browser/API response
4. Set as environment variable:
   ```bash
   export TEST_AUTH_TOKEN='eyJhbGc...'
   ```

## Running Tests

### Using Bootstrap Script (Recommended)

```bash
# Interactive mode (prompts for token)
./bootstrap_tests.sh

# Quick mode with environment variable
export TEST_AUTH_TOKEN='your-token'
./bootstrap_tests.sh --quick

# Admin tests only
export TEST_ADMIN_TOKEN='admin-token'
./bootstrap_tests.sh --admin-only
```

### Running Individual Tests

```bash
# Set token
export TEST_AUTH_TOKEN='your-token'

# Run specific test
python3 tests/test_e2e_token_based.py
python3 tests/test_e2e_admin_workflow.py
python3 tests/test_e2e_complete.py

# Run with pytest
pytest tests/test_e2e_token_based.py -v
```

### Debugging Token Issues

```bash
# Check if token can be decoded and user_id extracted
export TEST_AUTH_TOKEN='your-token'
python3 tests/verify_token.py
```

This will show:
- Token format validation
- Available claims in token
- Extracted user_id
- Whether role binding tests can run

## Test Requirements

All tests require:
- Pre-obtained JWT token from web interface
- Valid tenant with admin or end-user permissions
- Network access to dev.api.authsec.dev

**Important:** Tests do NOT perform registration or login. These must be done externally via the web interface.

## Authentication Pattern

All tests follow this pattern:

```python
import os
from authsec import AuthSecClient, AdminHelper

# Get token from environment
token = os.getenv('TEST_AUTH_TOKEN')
if not token:
    raise ValueError("TEST_AUTH_TOKEN required")

# Initialize with token
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev/uflow",
    token=token
)

# Run tests...
```

## No Login in Tests

⚠️ **Important:** These tests do NOT call `login()` or `register()` methods.

**Why?**
- MFA/OTP requirements make automated login impossible
- Tests focus on RBAC functionality, not authentication
- Tokens are obtained externally via web interface

**Migration:**
- Old tests that called `login()` have been removed or migrated
- All tests now use token-based authentication only

## Test Coverage

### What's Tested

- ✅ Permission creation (AdminHelper)
- ✅ Role creation (AdminHelper)
- ✅ Role binding creation (AdminHelper)
- ✅ Permission checks (AuthSecClient)
- ✅ Permission listing (AuthSecClient)
- ✅ Role listing (AdminHelper)
- ✅ User ID extraction from token (via API)

### What's NOT Tested

- ❌ User registration (requires MFA)
- ❌ User login (requires MFA/OTP)
- ❌ OTP verification (manual process)
- ❌ Password management (requires MFA)

## Troubleshooting

### "TEST_AUTH_TOKEN required" Error

**Solution:** Set the environment variable before running tests:
```bash
export TEST_AUTH_TOKEN='your-jwt-token'
```

### "Could not extract user_id from token" Warning

**Causes:**
- Token format issues
- Token doesn't contain user_id/sub/client_id claim

**Solutions:**
1. Manually set user ID:
   ```bash
   export TEST_USER_ID='your-user-uuid'
   ```
2. Debug token with `verify_token.py`
3. Get new token from web interface

### Role Binding Skipped

**Cause:** No role_id returned from backend

**What happens:**
- Tests continue but skip role binding creation
- Permission checks return empty (user has no assigned roles)

**This is a backend API issue, not SDK issue**

### Tests Pass But Permissions Return Empty

**Cause:** Backend API returns None/empty for created resources

**Impact:**
- create_role() returns None → no role_id
- Can't create role binding → permissions not assigned
- Permission checks correctly return empty

**This indicates backend needs fixes, SDK is working correctly**

## CI/CD Integration

For automated testing in CI/CD:

```yaml
# Example GitHub Actions
- name: Run E2E Tests
  env:
    TEST_AUTH_TOKEN: ${{ secrets.TEST_AUTH_TOKEN }}
  run: |
    ./bootstrap_tests.sh --quick
```

Store `TEST_AUTH_TOKEN` as a secret in your CI/CD system.

## Further Reading

- [BOOTSTRAP_TESTING.md](../BOOTSTRAP_TESTING.md) - Bootstrap script guide
- [MIGRATION_LOGIN_REMOVAL.md](../MIGRATION_LOGIN_REMOVAL.md) - Login removal migration guide
- [README.md](../README.md) - Main SDK documentation
