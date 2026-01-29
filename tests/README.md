# AuthSec SDK Tests

This directory contains integration tests for the AuthSec SDK.

## Test Files

### 1. `test_comprehensive.py` ✅ **No Dependencies Required**

**Comprehensive unit/integration tests** that validate SDK structure, imports, and method presence.

**What it tests:**
- SDK imports (`AuthSecClient`, `AdminHelper`)
- Method existence and signatures
- Configuration options
- Package structure
- Documentation accuracy

**Run it:**
```bash
python3 tests/test_comprehensive.py
```

**Status:** ✅ All tests passing (5/5)

---

### 2. `test_integration.py` ⚠️ **Requires Database**

**Full integration tests** against a live PostgreSQL database and running auth-manager service.

**Requirements:**
- PostgreSQL database running on `localhost:5433`
- Database: `authsec` (user: `authsec`, password: `authsec@kloudone`)
- Auth-manager service running (default: `http://localhost:7469`)

**What it tests:**
- Database setup and test data creation
- Real token generation with live database
- Permission checks against database
- Cleanup of test data

**Configure:**
```bash
export AUTH_MANAGER_URL="http://localhost:7469"  # Optional, defaults to localhost
```

**Run it:**
```bash
python3 tests/test_integration.py
```

---

### 3. `test_login.py` 🔐 **Requires Valid Credentials**

**Login authentication tests** against the real API.

**Requirements:**
- Valid user credentials in the system
- Running user-flow service (local or remote)

**Configure:**
```bash
export TEST_EMAIL="user@example.com"
export TEST_PASSWORD="your-password"
export TEST_CLIENT_ID="your-client-uuid"
export UFLOW_BASE_URL="https://dev.api.authsec.dev"  # or http://localhost:7468
```

**What it tests:**
- `login()` method with real credentials
- JWT token generation
- Token validation

**Run it:**
```bash
python3 tests/test_login.py
```

---

## Environment Configuration

Copy `.env.example` to `.env` and configure your test credentials:

```bash
cp tests/.env.example tests/.env
# Edit tests/.env with your credentials
```

**Example `.env`:**
```bash
# Admin token for API access
ADMIN_TOKEN=your-admin-jwt-token

# API endpoints
API_BASE_URL=https://dev.api.authsec.dev
ENDPOINT_TYPE=admin

# Test credentials
TEST_EMAIL=test@example.com
TEST_PASSWORD=test-password
TEST_CLIENT_ID=your-client-uuid
```

---

## Quick Start

### Run Basic Tests (No Setup Required)
```bash
python3 tests/test_comprehensive.py
```

### Run All Tests with Pytest
```bash
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=authsec --cov-report=html
```

---

## Token Expectations

Based on your original question, here's how tokens are handled:

### Integration Tests Approach:

1. **`test_comprehensive.py`**: ✅ **No real tokens needed** - Just validates structure
2. **`test_integration.py`**: 🔄 **Generates real tokens** - Creates test data in database, generates actual JWT tokens
3. **`test_login.py`**: 🔐 **Uses real tokens** - Requires valid user credentials, returns real JWT from API

### Token Generation Methods:

- **Real Authentication**: `client.login(email, password, client_id)` → Real JWT from API
- **OIDC Exchange**: `client.exchange_oidc(oidc_token)` → Real JWT from OIDC provider
- **Pre-existing Token**: `client = AuthSecClient(token="existing-jwt")` → Use existing token

### No Mocking

The SDK **does not use mocked tokens**. All integration tests use:
- Real database connections
- Real API calls
- Real JWT token generation
- Real authentication flows

---

## CI/CD Integration

For CI/CD pipelines, you can:

1. **Run basic tests** (no dependencies):
   ```bash
   python3 tests/test_comprehensive.py
   ```

2. **Run with test database**:
   ```bash
   # Setup test database
   docker run -d -p 5433:5432 -e POSTGRES_DB=authsec -e POSTGRES_USER=authsec -e POSTGRES_PASSWORD=authsec@kloudone postgres:14
   
   # Run integration tests
   python3 tests/test_integration.py
   ```

3. **Skip tests requiring credentials**:
   ```bash
   pytest tests/test_comprehensive.py -v
   ```

---

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running from the repository root:
```bash
cd /path/to/authz-sdk
python3 tests/test_comprehensive.py
```

### Database Connection Failures
Check that PostgreSQL is running:
```bash
psql -h localhost -p 5433 -U authsec -d authsec
```

### Authentication Failures
Verify your credentials are correct:
```bash
echo $TEST_EMAIL
echo $TEST_CLIENT_ID
# Don't echo password for security
```

---

## Test Summary

| Test File | Dependencies | Status | Purpose |
|-----------|-------------|--------|---------|
| `test_comprehensive.py` | None | ✅ Passing | Validate SDK structure |
| `test_integration.py` | PostgreSQL + Auth Manager | ⚠️ Needs setup | Full integration testing |
| `test_login.py` | Valid credentials | ⚠️ Needs config | Authentication testing |

**Next Steps:**
1. ✅ Run `test_comprehensive.py` - No setup needed
2. Configure database for `test_integration.py`
3. Set up test credentials for `test_login.py`
