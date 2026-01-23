# AuthSec SDK - Distribution Package

Official SDK for AuthSec authentication and role-based access control (RBAC).

[![PyPI version](https://badge.fury.io/py/authsec-authz-sdk.svg)](https://badge.fury.io/py/authsec-authz-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📚 Package Contents

This is a **complete distribution package** containing SDK code, documentation, tests, and examples:

### SDK Code
- **`authsec/`** - Python package with AuthSecClient and AdminHelper
  - `minimal.py` - AuthSecClient for authentication and authorization
  - `admin_helper.py` - AdminHelper for RBAC management
- **`pyproject.toml`** - Package metadata and configuration
- **`requirements.txt`** - Dependencies
- **`LICENSE`** - MIT License

### Tests
- **`tests/`** - Comprehensive unit test suite (44 tests)
  - `test_authsec_client.py` - Tests for AuthSecClient
  - `test_admin_helper.py` - Tests for AdminHelper
  - Run with: `python3 -m unittest discover tests -v`

### Examples
- **`examples/`** - Working code examples
  - `basic_auth.py` - Authentication and permission checking
  - `role_management.py` - Role assignment and management
  - `admin_rbac.py` - Complete RBAC workflow
  - `environment_config.py` - Environment configuration examples

### Documentation
1. **[README.md](README.md)** - This file: Overview and getting started
2. **[INSTALLATION.md](INSTALLATION.md)** - Installation and setup guide
3. **[AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)** - Complete guide for authentication and authorization using `AuthSecClient`
4. **[ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)** - Complete guide for RBAC management using `AdminHelper`
5. **[PUBLISHING.md](PUBLISHING.md)** - Guide for publishing to PyPI (for maintainers)
6. **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates

---

## 🚀 Quick Start

### Installation

```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

That's it! The package will be installed directly from GitHub.

**See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.**

### Python - Authentication Example

```python
from authsec import AuthSecClient

# Initialize client
client = AuthSecClient("https://api.authsec.dev")

# Login with credentials
token = client.login(
    email="user@example.com",
    password="your-password",
    client_id="your-client-id"
)

# Check permissions
if client.check_permission("document", "read"):
    print("✓ User can read documents")
```

### Python - Admin RBAC Example

```python
from authsec import AdminHelper

# Initialize with admin token
admin = AdminHelper(
    token="your-admin-token",
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
# Authentication
login(email, password, client_id) → str
exchange_oidc(code, client_id) → str

# Permission Checking
check_permission(resource, action) → bool
check_permission_scoped(resource, action, scope_type, scope_id) → bool

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

The SDK includes a comprehensive test suite with **44 unit tests** covering all functionality:

```bash
# Run all tests
python3 -m unittest discover tests -v

# Run specific test file
python3 -m unittest tests.test_authsec_client -v
python3 -m unittest tests.test_admin_helper -v

# Run with coverage (if pytest-cov installed)
pip install pytest pytest-cov
pytest tests/ --cov=authsec --cov-report=html
```

**Test Coverage:**
- ✅ Authentication (login, OIDC exchange, token verification)
- ✅ Permission checking (simple and scoped)
- ✅ Role management (create, update, delete, list)
- ✅ Role bindings (assign, remove, list)
- ✅ Permission management
- ✅ Scope management
- ✅ Error handling
- ✅ Environment configuration

### Code Examples

The `examples/` directory contains working examples for common use cases:

#### 1. Basic Authentication ([examples/basic_auth.py](examples/basic_auth.py))

```python
from authsec import AuthSecClient

# Login and check permissions
client = AuthSecClient("https://dev.api.authsec.dev")
token = client.login(email="user@example.com", password="pass", client_id="...")
can_read = client.check_permission("document", "read")
```

**Topics covered:**
- Client initialization
- Email/password login
- Permission checking
- Scoped permissions
- Pre-authenticated tokens
- OIDC token exchange

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

## 🎓 Getting Started Checklist

- [ ] Install SDK: `pip install git+https://github.com/authsec-ai/authz-sdk.git`
- [ ] Read [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md) for app integration
- [ ] Read [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md) for RBAC management
- [ ] Get your API credentials (client_id, tenant_id, admin_token)
- [ ] Configure environment variables
- [ ] Try the quick start examples (see `examples/` directory)
- [ ] Explore the API documentation at https://docs.authsec.dev

---

**Need Help?** Start with the documentation guide that matches your use case:
- Building an app? → [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)
- Managing RBAC? → [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)
