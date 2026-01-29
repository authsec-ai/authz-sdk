# AuthSec SDK

Official Python SDK for AuthSec authentication and role-based access control (RBAC).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Getting Started (3 Steps)

### Step 1: Install the SDK

```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

### Step 2: Set Up Your Environment

You need these credentials from your AuthSec dashboard:

```bash
# For regular authentication (AuthSecClient)
export AUTHSEC_API_URL="https://api.authsec.dev"
export AUTHSEC_CLIENT_ID="your-client-id"
export AUTHSEC_TENANT_ID="your-tenant-id"

# For admin operations (AdminHelper)
export AUTHSEC_ADMIN_TOKEN="your-admin-token"
```

**Or set them in your Python code:**

```python
import os
os.environ['AUTHSEC_API_URL'] = 'https://api.authsec.dev'
os.environ['AUTHSEC_CLIENT_ID'] = 'your-client-id'
os.environ['AUTHSEC_TENANT_ID'] = 'your-tenant-id'
```

### Step 3: Choose Your SDK

**Option A: Use `AuthSecClient` for Authentication & Authorization**
- For application developers
- Handle user login, check permissions
- See [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)

**Option B: Use `AdminHelper` for RBAC Management**
- For administrators and DevOps
- Create roles, manage permissions, assign user access
- See [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)

---

## 📖 Complete Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Installation details
- **[AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)** - AuthSecClient guide
- **[ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)** - AdminHelper guide
- **[README_E2E_TESTS.md](README_E2E_TESTS.md)** - E2E testing guide
- **[examples/](examples/)** - Working code examples

---

## 🎯 Quick Examples

### AuthSecClient - User Authentication

```python
from authsec import AuthSecClient
import os

# Initialize with pre-obtained token
# Get your token from: https://app.authsec.dev
client = AuthSecClient(
    base_url=os.getenv('AUTHSEC_API_URL'),
    token=os.getenv('AUTHSEC_TOKEN'),  # JWT token from dashboard
    endpoint_type="enduser"  # or "admin" for admin operations
)

# Check permissions
if client.check_permission("document", "read"):
    print("✓ User can read documents")

# List user permissions
permissions = client.list_permissions()
for perm in permissions:
    print(f"Resource: {perm['resource']}, Actions: {perm['actions']}")
```

**Authentication Note:** Login requires OTP/MFA verification and must be done through the web interface at https://app.authsec.dev. Once authenticated, copy your JWT token and use it to initialize the SDK.

**Next Steps:** Read [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md) for complete usage.

### AdminHelper - RBAC Management

```python
from authsec import AdminHelper
import os

# Initialize with admin token
admin = AdminHelper(
    token=os.getenv('AUTHSEC_ADMIN_TOKEN'),
    endpoint_type="admin"
)

# Create a role with permissions
role = admin.create_role(
    name="Editor",
    description="Can read and write documents",
    permission_strings=["document:read", "document:write"]
)

# Assign role to user
binding = admin.create_role_binding(
    user_id="user-uuid",
    role_id=role['id']
)
```

**Next Steps:** Read [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md) for complete RBAC management.

---

## 🎯 Features

### Authentication & Authorization (`AuthSecClient`)
- 🔐 **User Authentication**: Email/password login, OIDC token exchange
- 🎫 **JWT Token Management**: Generate, verify, and manage JWT tokens
- 🔑 **Permission Checking**: Granular resource:action permission validation
- 🌐 **Scoped Permissions**: Tenant and project-scoped authorization
- 🔄 **Token Lifecycle**: Automatic token injection in API requests
- 👥 **Role Assignment**: Assign and manage user roles

### RBAC Management (`AdminHelper`)
- 🎭 **Role Management**: Create, update, list, and delete roles
- 📋 **Permission Management**: Create and manage fine-grained permissions
- 🔗 **Role Bindings**: Assign roles to users with scoping
- 🎯 **Scope Management**: Create and manage resource scopes
- 🔐 **Secret Management**: Create and manage application secrets
- 🏢 **Multi-tenant Support**: Admin and tenant-specific operations

---

## 📖 Documentation Guides

### For Application Developers

If you're building an application and need authentication/authorization:

👉 **Read:** [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)

**Topics covered:**
- SDK initialization and configuration
- User login and token management
- OIDC integration
- Permission checking (resource:action)
- Scoped permission validation
- Role assignment to users
- Making authenticated API requests
- Error handling
- Complete code examples

### For Administrators & DevOps

If you're managing RBAC resources (roles, permissions, bindings):

👉 **Read:** [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)

**Topics covered:**
- AdminHelper initialization
- Creating and managing roles
- Permission management
- Role binding management
- Scope management
- Endpoint types (admin vs enduser)
- Batch operations
- Secret management
- Integration examples
- Testing and troubleshooting

---

## 🔧 SDK Components

### `AuthSecClient` - Authentication & Authorization

**Use Case:** Application authentication and permission checking

**Target Users:** Application developers integrating auth into their apps

**Core Methods:**
```python
# Authentication (Note: login via web interface required due to OTP/MFA)
exchange_oidc(code, client_id) → str

# Permission Checking
check_permission(resource, action) → bool
check_permission_scoped(resource, action, scope_type, scope_id) → bool
list_permissions() → list

# Role Management (End-user)
assign_role(user_id, role_id) → dict
list_role_bindings(user_id=None) → list
remove_role_binding(binding_id) → bool
```

### `AdminHelper` - RBAC Management

**Use Case:** Administrative RBAC resource management

**Target Users:** System administrators, DevOps teams

**Core Methods:**
```python
# Role Management
create_role(name, permission_strings) → dict
list_roles(resource=None, user_id=None) → list
update_role(role_id, permission_strings) → dict
delete_role(role_id) → bool

# Role Bindings
create_role_binding(user_id, role_id, scope_type=None, scope_id=None) → dict
list_role_bindings(user_id=None, role_id=None) → list
remove_role_binding(binding_id) → bool

# Permissions
create_permission(resource, action, description=None) → dict
list_permissions(resource=None) → list

# Scopes
create_scope(name, description, resources) → dict
list_scopes() → list
```

---

## 🌐 Environment Configuration

Both SDKs support environment variable configuration:

```bash
# Authentication SDK
export AUTH_BASE_URL="https://api.authsec.dev"
export CLIENT_ID="your-client-id"

# Admin SDK
export ADMIN_TOKEN="your-admin-token"
export ADMIN_BASE_URL="https://api.authsec.dev"
export ENDPOINT_TYPE="admin"  # or "enduser"
export ADMIN_TIMEOUT="10"
```

**Load from environment:**

```python
from authsec import AuthSecClient, AdminHelper

# Authentication client (reads AUTH_BASE_URL)
client = AuthSecClient.from_env()

# Admin helper (reads ADMIN_TOKEN, ADMIN_BASE_URL, ENDPOINT_TYPE)
admin = AdminHelper.from_env()
```

---

## 🔐 Endpoint Types

The SDK supports two operational modes:

### Admin Endpoints (`endpoint_type="admin"`)

- **Purpose:** Platform-level RBAC management
- **Database:** Primary admin database
- **Endpoint Prefix:** `/uflow/admin/*`
- **Use Case:** System-wide role and permission management

```python
admin = AdminHelper(
    token="admin-token",
    endpoint_type="admin"
)
```

### End-User Endpoints (`endpoint_type="enduser"`)

- **Purpose:** Tenant-specific RBAC management
- **Database:** Tenant database
- **Endpoint Prefix:** `/uflow/enduser/*`
- **Use Case:** Tenant-scoped operations (default)

```python
admin = AdminHelper(
    token="user-token",
    endpoint_type="enduser"  # default
)
```

---

## 📦 Installation & Requirements

### Python

**Requirements:**
- Python 3.7 or higher
- `requests` library (auto-installed)

**Installation:**
```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

---

## 🛠️ Error Handling

Both SDKs provide comprehensive error handling:

```python
from authsec import AdminHelper
from authsec.admin_helper import AdminSDKError, RoleBindingError

try:
    admin = AdminHelper(token="token")
    role = admin.create_role("Test Role", ["doc:read"])
except RoleBindingError as e:
    print(f"Role binding error: {e}")
except AdminSDKError as e:
    print(f"API error: {e.status_code} - {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**Common Error Types:**
- `AdminSDKError` - Base SDK error
- `RoleBindingError` - Role binding specific errors
- `PermissionError` - Permission-related errors
- `AuthenticationError` - Authentication failures

---

## 📚 Additional Resources

### Documentation
- **API Reference**: https://docs.authsec.dev
- **API Interactive Docs**: https://dev.api.authsec.dev/uflow/redoc
- **Swagger UI**: https://dev.api.authsec.dev/uflow/docs

### Source Code
- **Python SDK**: https://github.com/authsec-ai/authz-sdk
- **Auth Manager**: https://github.com/authsec-ai/auth-manager

### Package Registries
- **PyPI**: https://pypi.org/project/authsec-authz-sdk/

### Support
- **Issues**: GitHub repository issues
- **Email**: support@authsec.dev
- **Documentation**: https://docs.authsec.dev

---

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---


## 🧪 Testing & Examples

### Running Tests

The SDK includes integration tests that validate all functionality.

**Quick Start - Run Tests Without Setup:**
```bash
# Run comprehensive tests (no dependencies required)
./tests/run_tests.sh comprehensive

# Or run directly
python3 tests/test_comprehensive.py
```

**All Test Options:**
```bash
# Run comprehensive tests (no setup needed) ✅
./tests/run_tests.sh comprehensive

# Run integration tests (requires PostgreSQL)
./tests/run_tests.sh integration

# Run login tests (requires valid credentials)
./tests/run_tests.sh login

# Run all tests with pytest
./tests/run_tests.sh pytest
```

**Using pytest:**
```bash
# Install pytest if needed
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=authsec --cov-report=html
```

**Test Coverage:**
- ✅ SDK imports and structure
- ✅ Method signatures and existence
- ✅ Configuration options
- ✅ Package structure validation
- ✅ Documentation accuracy
- ⚠️ Authentication (requires credentials)
- ⚠️ Permission checking (requires database)
- ⚠️ Role management (requires database)

**See [tests/README.md](tests/README.md) for detailed test documentation.**

## ⚡ Automated Testing (Quickest Way)

Run tests with **zero manual setup**:

```bash
# Full automated bootstrap (creates venv, installs deps, runs tests)
./bootstrap_tests.sh

# Quick tests only (no API calls)
./bootstrap_tests.sh --quick

# Clean rebuild
./bootstrap_tests.sh --clean
```

The bootstrap script automatically:
- ✅ Creates virtual environment
- ✅ Installs SDK in development mode
- ✅ Installs all test dependencies
- ✅ Runs complete test suite

**See [TESTING_QUICKSTART.md](TESTING_QUICKSTART.md) for detailed automated testing guide.**

---

## 🧪 End-to-End Testing

### Token-Based E2E Tests ✅ RECOMMENDED

The SDK includes comprehensive token-based E2E tests that validate all functionality without complex setup.

```bash
# Get a token from your dashboard or login
export TEST_AUTH_TOKEN='your-jwt-token'

# Run comprehensive E2E tests
python3 tests/test_e2e_token_based.py

# Or run only admin tests
python3 tests/test_e2e_token_based.py --admin-only

# Or run only end-user tests
python3 tests/test_e2e_token_based.py --enduser-only
```

**What Gets Tested:**
- ✅ 6 Admin operations (create/list permissions & roles, permission checks)
- ✅ 2 End-user operations (list permissions, check permissions)
- ✅ Full integration with live API
- ✅ Real database persistence
- ✅ Cross-SDK verification (AdminHelper writes, AuthSecClient reads)

**See [README_E2E_TESTS.md](README_E2E_TESTS.md) for complete E2E testing guide.**

---

## 🔒 Security

### Security Architecture

✅ **Zero Direct Database Access** - SDK only makes HTTPS API calls  
✅ **No Hardcoded Credentials** - All tokens via environment variables  
✅ **HTTPS Only** - All communication encrypted  
✅ **Bearer Token Auth** - Industry-standard JWT authentication  
✅ **No Injection Risks** - JSON payloads, no SQL construction

**Security Score: 9/10** - Production ready

**Architecture:**
```
SDK (authsec/) 
  ↓ HTTPS Only
API Layer (dev.api.authsec.dev)
  ↓ Internal
Database (Tenant DB)
```

### Best Practices

```python
# ✅ GOOD: Token from environment
import os
token = os.getenv('AUTHSEC_TOKEN')
client = AuthSecClient(base_url=url, token=token)

# ❌ BAD: Hardcoded token
client = AuthSecClient(token='eyJhbGci...')  # Never do this!

# ✅ GOOD: HTTPS endpoints
base_url = "https://dev.api.authsec.dev"

# ❌ BAD: HTTP endpoints
base_url = "http://dev.api.authsec.dev"  # Insecure!
```

**For full security audit, see:** [Security Audit Report](https://github.com/authsec-ai/authz-sdk/security/audit)

---

## 📊 Test Results

Latest E2E test run (2026-01-28):
```
Admin Operations:
  Passed (6):
    ✓ create_permission
    ✓ list_permissions
    ✓ create_role
    ✓ list_roles
    ✓ check_permission
    ✓ list_user_permissions

End-User Operations:
  Passed (2):
    ✓ list_permissions
    ✓ check_permission

Overall: Total Passed: 8, Total Failed: 0

✓✓✓ ALL TESTS PASSED!
```

**See [TESTING_QUICKSTART.md](TESTING_QUICKSTART.md) for detailed automated testing guide.**

### Code Examples

The `examples/` directory contains working examples for common use cases:

#### 1. Basic Authentication ([examples/basic_auth.py](examples/basic_auth.py))

```python
from authsec import AuthSecClient

# Initialize with token (obtained from https://app.authsec.dev)
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev",
    token="your-jwt-token-here"
)

# Check permissions
can_read = client.check_permission("document", "read")
```

**Topics covered:**
- Client initialization with token
- Permission checking
- Scoped permissions
- OIDC token exchange (if applicable)

#### 2. Role Management ([examples/role_management.py](examples/role_management.py))

```python
# Assign roles to users
binding = client.assign_role(user_id, role_id)

# Scoped role assignment
scoped_binding = client.assign_role(
    user_id, role_id,
    scope_type="project",
    scope_id=project_id
)

# List and manage bindings
bindings = client.list_role_bindings(user_id=user_id)
```

**Topics covered:**
- Role assignment
- Scoped roles
- Conditional roles
- Admin vs user endpoints
- Listing role bindings

#### 3. Admin RBAC Management ([examples/admin_rbac.py](examples/admin_rbac.py))

```python
from authsec import AdminHelper

admin = AdminHelper(token="admin-token", endpoint_type="enduser")

# Create permissions
perm = admin.create_permission("document", "write", "Write documents")

# Create role with permissions
role = admin.create_role(
    "Editor",
    description="Can edit documents",
    permission_strings=["document:read", "document:write"]
)

# Assign to user
binding = admin.create_role_binding(user_id, role['id'])
```

**Topics covered:**
- Permission creation
- Role creation and management
- Role bindings
- Scope management
- Admin vs enduser endpoints
- Batch operations

#### 4. Environment Configuration ([examples/environment_config.py](examples/environment_config.py))

```python
# Using environment variables
admin = AdminHelper.from_env()

# Multi-environment configuration
# Production secret management
# Using .env files
```

**Topics covered:**
- Environment variable configuration
- .env file usage
- Production secret management
- Multi-environment setup

### Running Examples

```bash
# Run an example
cd examples
python3 basic_auth.py
python3 role_management.py
python3 admin_rbac.py
python3 environment_config.py
```

**Note:** Update the examples with your actual credentials before running.

---

## ✅ Getting Started Checklist

- [ ] **Install**: Run `pip install git+https://github.com/authsec-ai/authz-sdk.git`
- [ ] **Get Credentials**: Obtain from AuthSec dashboard:
  - API URL
  - Client ID
  - Tenant ID  
  - Admin Token (for RBAC operations)
- [ ] **Set Environment Variables**: Export credentials as env vars
- [ ] **Choose Your Path**:
  - Building an app? → Use `AuthSecClient` ([guide](AUTHENTICATION_AUTHORIZATION_GUIDE.md))
  - Managing access? → Use `AdminHelper` ([guide](ADMIN_HELPER_GUIDE.md))
- [ ] **Run Examples**: Try code in `examples/` directory
- [ ] **Explore API Docs**: https://docs.authsec.dev

---

**Need Help?** Start with the documentation guide that matches your use case:
- Building an app? → [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)
- Managing RBAC? → [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)
