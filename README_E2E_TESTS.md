# End-to-End Testing Guide

## Token-Based E2E Tests

The SDK includes comprehensive token-based E2E tests that validate all functionality without requiring the full registration/login flow.

### Quick Start

```bash
# Get a token from your dashboard or login flow
export TEST_AUTH_TOKEN='your-jwt-token-here'

# Run all tests
python3 tests/test_e2e_token_based.py

# Run only admin tests
python3 tests/test_e2e_token_based.py --admin-only

# Run only end-user tests
python3 tests/test_e2e_token_based.py --enduser-only
```

### What Gets Tested

#### Admin Operations
- ✅ Token verification
- ✅ Create permissions
- ✅ List all permissions
- ✅ Create roles with permissions
- ✅ List all roles
- ✅ Get role by ID
- ✅ Check permission access
- ✅ List user permissions

#### End-User Operations
- ✅ Token verification
- ✅ List user permissions
- ✅ Check specific permission access

### Getting a Token

#### Option 1: From Dashboard
1. Login to https://app.authsec.dev
2. Open browser DevTools → Application → Local Storage
3. Find your JWT token
4. Export it: `export TEST_AUTH_TOKEN='...'`

#### Option 2: Programmatically
```bash
# Use existing login credentials
python3 tests/debug_login.py
# Extract token from response
```

#### Option 3: From Previous Tests
```bash
# Run registration flow (if it works in your environment)
python3 tests/test_register_login.py
# Extract token from output
```

### Expected Output

```
======================================================================
Admin Operations Test Suite
======================================================================

Step 1: Verify Token
✓ Token verified
ℹ User ID: 123e4567-e89b-12d3-a456-426614174000
ℹ Email: admin@example.com

Step 2: Create Permissions
✓ Created: test_resource_abc123:read
✓ Created: test_resource_abc123:write
...

======================================================================
Test Summary
======================================================================

Admin Operations:
  Passed (8):
    ✓ verify_token
    ✓ create_permission
    ✓ list_permissions
    ✓ create_role
    ✓ list_roles
    ✓ get_role
    ✓ check_permission
    ✓ list_user_permissions

======================================================================
✓✓✓ ALL TESTS PASSED!
======================================================================
```

### Advanced Usage

#### Separate Admin and End-User Tokens
```bash
export TEST_ADMIN_TOKEN='admin-jwt-here'
export TEST_ENDUSER_TOKEN='enduser-jwt-here'
python3 tests/test_e2e_token_based.py
```

#### Custom API URL
```bash
python3 tests/test_e2e_token_based.py --base-url https://staging.api.authsec.dev
```

### Troubleshooting

**"No auth token found!"**
- Make sure you've exported the token: `export TEST_AUTH_TOKEN='...'`
- Token must be a valid JWT

**"Token verification failed"**
- Token may be expired
- Token may be for wrong environment (dev vs prod)
- Get a fresh token

**"Permission checks return False"**
- This is normal! It shows the permission check works
- Tests verify the SDK methods work, not that you have specific permissions

### CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run E2E Tests
  env:
    TEST_AUTH_TOKEN: ${{ secrets.AUTHSEC_TEST_TOKEN }}
  run: |
    python3 tests/test_e2e_token_based.py
```

## Other E2E Test Files

- `test_e2e_simplified.py` - Registration flow test (requires working registration API)
- `test_e2e_final.py` - Complete flow test (requires OTP)
- `test_e2e_admin _workflow.py` - Full workflow (currently blocked by API issues)

**Recommendation:** Use `test_e2e_token_based.py` for reliable, repeatable testing.
