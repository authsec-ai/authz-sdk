# AuthSec SDK - Complete Guide

Official Python SDK for AuthSec authentication and role-based access control (RBAC).

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> **Quick Navigation:** [Installation](#installation) | [Quick Start](#quick-start) | [AuthSecClient](#authsecclient-guide) | [AdminHelper](#adminhelper-guide) | [Examples](#examples) | [Testing](tests/README.md)

---

## Table of Contents

1.  [Installation](#installation)
2. [Quick Start](#quick-start)
3. [AuthSecClient Guide](#authsecclient-guide) - Authentication & Authorization
4. [AdminHelper Guide](#adminhelper-guide) - RBAC Management
5. [API Reference](#api-reference)
6. [Complete Examples](#complete-examples)
7. [Testing](tests/README.md)
8. [Publishing](PUBLISHING.md)

---

## Installation

### Install via pip

```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

**Requirements:**
- Python 3.7 or higher
- `requests` library (auto-installed)

### Verify Installation

```python
from authsec import AuthSecClient, AdminHelper
print("✓ AuthSec SDK imported successfully")
```

---

## Quick Start 

### Option A: Authentication & Authorization (AuthSecClient)

For application developers implementing auth in their apps:

```python
from authsec import AuthSecClient
import os

# Initialize with pre-obtained token
# Get token from: https://app.authsec.dev
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev",
    token=os.getenv('AUTHSEC_TOKEN'),
    endpoint_type="enduser"  # or "admin"
)

# Check permissions
if client.check_permission("document", "read"):
    print("✓ User can read documents")

# List permissions
permissions = client.list_permissions()
for perm in permissions:
    print(f"{perm['resource']}: {perm['actions']}")
```

### Option B: RBAC Management (AdminHelper)

For administrators managing roles and permissions:

```python
from authsec import AdminHelper
import os

# Initialize with admin token
admin = AdminHelper(
    token=os.getenv('AUTHSEC_ADMIN_TOKEN'),
    base_url="https://dev.api.authsec.dev"
)

# Create permission
perm = admin.create_permission("document", "read", "Read documents")

# Create role with permissions
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

## AuthSecClient Guide

### Overview

`AuthSecClient` handles authentication and authorization for your applications.

**Key Features:**
- 🔐 Token-based authentication
- 🔑 Permission checking (resource:action)
- 🌐 Scoped permissions (tenant/project)
- 👥 Role assignment
- 🔄 Authenticated API requests

### Initialization

```python
from authsec import AuthSecClient

# Basic initialization
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev",
    token="your-jwt-token"
)

# With options
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev",
    token="your-token",
    timeout=10.0,
    endpoint_type="enduser"  # or "admin"
)
```

### Authentication

**Note:** Login requires OTP/MFA verification and must be done through the web interface at https://app.authsec.dev. Once authenticated, copy your JWT token.

```python
# Method 1: Initialize with token
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev",
    token="eyJhbGc..."
)

# Initialize with token
client.set_token("eyJhbGc...")

# Token is automatically used in all API calls
# No verification method needed - token validity checked by backend
```

### Permission Checking

#### Basic Permission Check

```python
# Check if user has permission
if client.check_permission("document", "read"):
    # User authorized
    documents = fetch_documents()
else:
    raise PermissionError("Access denied")
```

#### Scoped Permission Check

```python
# Check permission within specific scope
can_write = client.check_permission_scoped(
    resource="document",
    action="write",
    scope_type="project",
    scope_id="project-uuid"
)
```

#### List All Permissions

```python
perms = client.list_permissions()
# Returns: [{"resource": "document", "actions": ["read", "write"]}, ...]

for perm in perms:
    print(f"{perm['resource']}: {', '.join(perm['actions'])}")
```

### Role Assignment

```python
# Assign role to user (tenant-wide)
binding = client.assign_role(
    user_id="user-uuid",
    role_id="role-uuid"
)

# Scoped role assignment
binding = client.assign_role(
    user_id="user-uuid",
    role_id="role-uuid",
    scope_type="project",
    scope_id="project-uuid"
)
```

### Authenticated Requests

```python
# SDK automatically injects token in Authorization header
response = client.request("GET", "/api/documents")
documents = response.json()

# POST request
response = client.request(
    "POST",
    "/api/documents",
    json={"title": "New Doc"}
)
```

### Permission-Based Decorator Pattern

```python
from functools import wraps

def require_permission(resource, action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not client.check_permission(resource, action):
                raise PermissionError(f"Missing: {resource}:{action}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_permission("invoice", "create")
def create_invoice(data):
    return save_invoice(data)
```

---

## AdminHelper Guide

### Overview

`AdminHelper` provides complete RBAC management capabilities.

**Key Features:**
- 🎭 Role CRUD operations
- 📋 Permission CRUD operations
- 🔗 Role binding management
- 👥 User management
- 🏢 Multi-tenant support

### Initialization

```python
from authsec import AdminHelper

# Basic initialization
admin = AdminHelper(
    token="admin-token",
    base_url="https://dev.api.authsec.dev"
)

# With endpoint type
admin = AdminHelper(
    token="admin-token",
    base_url="https://dev.api.authsec.dev",
    endpoint_type="admin"  # or "enduser" (default)
)
```

---

## Testing

The SDK includes comprehensive integration tests that validate SDK wrapper methods work correctly.

### Test Philosophy

These are **SDK integration tests** - they validate that the SDK methods in `minimal.py` and `admin_helper.py` correctly call backend endpoints. Tests verify:

✅ SDK methods execute without errors  
✅ SDK correctly formats requests to backend APIs  
✅ SDK properly handles backend responses  
❌ **NOT** testing backend API implementation or business logic

### Running Tests

#### Quick Test

```bash
# Set your token
export TEST_AUTH_TOKEN='your-jwt-token'

# Run primary E2E test
python3 tests/test_e2e_token_based.py
```

#### Comprehensive Test Suite

```bash
# Run all tests via bootstrap script
./bootstrap_tests.sh

# Or with pytest
pytest tests/ -v
```

### Test Coverage

#### Core SDK Methods Tested

**AuthSecClient** (`minimal.py`):
- ✅ `register()` - Admin registration with OTP
- ✅ `verify_registration()` - OTP verification
- ✅ `register_enduser()` - End-user registration
- ✅ `verify_enduser_registration()` - End-user OTP verification
- ✅ `exchange_oidc()` - OIDC token exchange
- ✅ `check_permission()` - Permission validation
- ✅ `check_permission_scoped()` - Scoped permissions
- ✅ `list_permissions()` - List user permissions
- ✅ `assign_role()` - Role binding creation
- ✅ `list_role_bindings()` - List role assignments
- ✅ `remove_role_binding()` - Remove role assignments

**AdminHelper** (`admin_helper.py`):
- ✅ `create_permission()` - Permission creation
- ✅ `list_permissions()` - Permission listing
- ✅ `create_role()` - Role creation with permissions
- ✅ `list_roles()` - Role listing
- ✅ `get_role()` - Fetch role details
- ✅ `update_role()` - Update role permissions
- ✅ `delete_role()` - Role deletion
- ✅ `create_role_binding()` - Assign roles to users
- ✅ `list_role_bindings()` - List user role assignments
- ✅ `remove_role_binding()` - Remove role assignments

#### Test Files

| Test File | Purpose | Coverage |
|-----------|---------|----------|
| `test_comprehensive.py` | SDK structure validation | Package imports, method existence |
| `test_endpoint_validation.py` | Endpoint existence validation | All 7 SDK endpoints |
| `test_registration_oidc.py` | Registration flows | Admin/enduser registration, OIDC |
| `test_e2e_token_based.py` | Primary E2E integration | Full RBAC workflow |
| `test_e2e_admin_workflow.py` | Admin operations | Role/permission management |
| `test_e2e_complete.py` | Simplified RBAC test | Permission checks |

### Test Configuration

```bash
# Required
export TEST_AUTH_TOKEN='your-jwt-token'

# Optional
export TEST_BASE_URL='https://your-domain.com/api'  # Default: dev environment
export TEST_USER_ID='user-uuid'  # Manual override (auto-extracted from JWT)
```

### Understanding Test Results

Tests validate **SDK functionality**, not backend behavior:

```
✓ SDK method executed successfully
  - SDK made correct API call
  - SDK handled response properly
  - Test PASSES

⚠ Backend returned empty response (SDK worked correctly)
  - SDK executed without error
  - Backend didn't return data (backend issue, not SDK)
  - Test still PASSES
```

### More Information

See [tests/README.md](tests/README.md) for:
- Detailed test documentation
- Custom domain testing
- CI/CD integration
- Troubleshooting guides

---

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

---

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

---

## Support

- **Documentation:** This README and [tests/README.md](tests/README.md)
- **Issues:** https://github.com/authsec-ai/authz-sdk/issues
- **Email:** support@authsec.dev

---

## Changelog

### Latest Version

**Latest Version:**
- **Fixed:** Updated `AdminHelper` to use correct RBAC endpoints (`/uflow/user/rbac/*`) for end-user mode
- **Fixed:** Improved handling of list responses for permissions, roles, and bindings
- **Removed Methods:**
- `login()` - Use web interface at https://app.authsec.dev for authentication
- `verify_token()` - User ID now extracted locally from JWT (no API call needed)

**Testing:**
- Added comprehensive SDK integration tests
- 100% SDK method coverage
- Tests validate SDK wrapper functionality, not backend APIs

**See:** [PUBLISHING.md](PUBLISHING.md) for version history

### Permission Management

#### Create Permissions

```python
# Single permission
perm = admin.create_permission(
    resource="document",
    action="read",
    description="Read documents"
)

# Batch create
resources = {
    "document": ["read", "write", "delete"],
    "invoice": ["read", "create", "approve"],
}

for resource, actions in resources.items():
    for action in actions:
        admin.create_permission(resource, action)
```

#### List Permissions

```python
# All permissions
perms = admin.list_permissions()

# Filter by resource
doc_perms = admin.list_permissions(resource="document")
```

#### Delete Permission

```python
admin.delete_permission(permission_id)
```

### Role Management

#### Create Roles

```python
# Create role with permissions
role = admin.create_role(
    name="Editor",
    description="Document editor",
    permission_strings=["document:read", "document:write"]
)

print(f"Created role: {role['id']}")
```

#### List Roles

```python
# All roles
roles = admin.list_roles()

# Filter by user
user_roles = admin.list_roles(user_id="user-uuid")
```

#### Get Role Details

```python
role = admin.get_role(role_id)
print(f"Name: {role['name']}")
print(f"Permissions: {role.get('permissions', [])}")
```

#### Update Role

```python
updated = admin.update_role(
    role_id=role_id,
    permission_strings=["document:read", "document:write", "document:delete"]
)
```

#### Delete Role

```python
admin.delete_role(role_id)
```

### Role Binding Management

#### Create Bindings

```python
# Tenant-wide binding
binding = admin.create_role_binding(
    user_id="user-uuid",
    role_id="role-uuid"
)

# Scoped binding
binding = admin.create_role_binding(
    user_id="user-uuid",
    role_id="role-uuid",
    scope_type="project",
    scope_id="project-uuid"
)

# Conditional binding
binding = admin.create_role_binding(
    user_id="user-uuid",
    role_id="admin-role-uuid",
    conditions={"mfa_required": True}
)
```

#### List Bindings

```python
# All bindings
bindings = admin.list_role_bindings()

# User-specific
user_bindings = admin.list_role_bindings(user_id="user-uuid")

# Role-specific
role_bindings = admin.list_role_bindings(role_id="role-uuid")
```

#### Delete Bindings

```python
# Single binding
admin.delete_role_binding(binding_id)

# All bindings for a user
admin.delete_user_bindings(user_id)
```

### User Management

```python
# List all users
users = admin.list_users()

# Get user details
user = admin.get_user(user_id)
```

### Complete RBAC Setup Workflow

```python
from authsec import AdminHelper

# Initialize
admin = AdminHelper(token="admin-token", base_url="https://dev.api.authsec.dev")

# 1. Create permissions
perms = {
    "document": ["read", "write", "delete"],
    "invoice": ["read", "create", "approve"]
}

for resource, actions in perms.items():
    for action in actions:
        admin.create_permission(resource, action)

# 2. Create roles
roles = {
    "Viewer": ["document:read", "invoice:read"],
    "Editor": ["document:read", "document:write", "invoice:read"],
    "Admin": ["document:*", "invoice:*"]  # All permissions
}

created_roles = {}
for name, perm_strings in roles.items():
    role = admin.create_role(
        name=name,
        description=f"{name} role",
        permission_strings=perm_strings
    )
    created_roles[name] = role

# 3. Assign roles to users
admin.create_role_binding(
    user_id="alice-uuid",
    role_id=created_roles["Editor"]['id']
)

admin.create_role_binding(
    user_id="bob-uuid",
    role_id=created_roles["Viewer"]['id']
)

print("✓ RBAC setup complete!")
```

---

## API Reference

### AuthSecClient Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `__init__(base_url, token=None, ...)` | Initialize client | AuthSecClient |
| `set_token(token)` | Set authentication token | None |
| `check_permission(resource, action)` | Check permission | bool |
| `check_permission_scoped(...)` | Check scoped permission | bool |
| `list_permissions()` | List user permissions | list |
| `assign_role(user_id, role_id, ...)` | Assign role to user | dict |
| `request(method, url, **kwargs)` | Make authenticated request | Response |

### AdminHelper Methods

#### Permission Management

| Method | Description | Returns |
|--------|-------------|---------|
| `create_permission(resource, action, description=None)` | Create permission | dict |
| `list_permissions(resource=None)` | List permissions | list |
| `get_permission(permission_id)` | Get permission details | dict |
| `delete_permission(permission_id)` | Delete permission | bool |

#### Role Management

| Method | Description | Returns |
|--------|-------------|---------|
| `create_role(name, description=None, permission_strings=None)` | Create role | dict |
| `list_roles(resource=None, user_id=None)` | List roles | list |
| `get_role(role_id)` | Get role details | dict |
| `update_role(role_id, ...)` | Update role | dict |
| `delete_role(role_id)` | Delete role | bool |

#### Role Binding Management

| Method | Description | Returns |
|--------|-------------|---------|
| `create_role_binding(user_id, role_id, ...)` | Create binding | dict |
| `list_role_bindings(user_id=None, role_id=None)` | List bindings | list |
| `get_role_binding(binding_id)` | Get binding details | dict |
| `delete_role_binding(binding_id)` | Delete binding | bool |
| `delete_user_bindings(user_id)` | Delete all user bindings | bool |

#### User Management

| Method | Description | Returns |
|--------|-------------|---------|
| `list_users()` | List all users | list |
| `get_user(user_id)` | Get user details | dict |

---

## Complete Examples

### Example 1: Basic Application with Auth

```python
from authsec import AuthSecClient
import os

# Initialize
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev",
    token=os.getenv('AUTH_TOKEN')
)

# Check before allowing action
def delete_document(doc_id):
    if not client.check_permission("document", "delete"):
        return {"error": "Permission denied"}, 403
    
    # Delete document
    return {"status": "deleted", "id": doc_id}, 200

# List what user can do
def get_user_capabilities():
    perms = client.list_permissions()
    capabilities = []
    
    for perm in perms:
        for action in perm['actions']:
            capabilities.append(f"{perm['resource']}:{action}")
    
    return capabilities
```

### Example 2: Multi-Tenant RBAC Setup

```python
from authsec import AdminHelper

# Initialize for tenant-level operations
admin = AdminHelper(
    token=tenant_admin_token,
    base_url="https://dev.api.authsec.dev",
    endpoint_type="enduser"  # Tenant-specific DB
)

# Setup RBAC for a new tenant
def setup_tenant_rbac():
    # Create permissions
    permissions = [
        ("document", "read"), ("document", "write"), ("document", "delete"),
        ("user", "read"), ("user", "invite"),
        ("settings", "read"), ("settings", "write")
    ]
    
    for resource, action in permissions:
        admin.create_permission(resource, action)
    
    # Create roles
    member_role = admin.create_role(
        "Member",
        permission_strings=["document:read", "document:write", "user:read"]
    )
    
    admin_role = admin.create_role(
        "Admin",
        permission_strings=["document:*", "user:*", "settings:*"]
    )
    
    return {"member": member_role, "admin": admin_role}
```

### Example 3: Permission-Based API Middleware

```python
from functools import wraps
from flask import request, jsonify

def require_permission(resource, action):
    """Flask decorator for permission checking"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from request
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Initialize client
            client = AuthSecClient(
                base_url="https://dev.api.authsec.dev",
                token=token
            )
            
            # Check permission
            if not client.check_permission(resource, action):
                return jsonify({"error": "Permission denied"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage in Flask routes
@app.route('/api/documents/<doc_id>', methods=['DELETE'])
@require_permission("document", "delete")
def delete_document(doc_id):
    # Only executes if user has document:delete permission
    return {"status": "deleted"}
```

---

## Testing

See [tests/README.md](tests/README.md) for comprehensive testing guide with custom domain URL support.

**Quick Start:**
```bash
# Get token from https://app.authsec.dev
export TEST_AUTH_TOKEN='your-token'

# Optional: Test against your domain
export TEST_BASE_URL='https://your-domain.com/api'

# Run tests
python3 tests/test_e2e_token_based.py
```

---

## Publishing

See [PUBLISHING.md](PUBLISHING.md) for instructions on publishing to PyPI.

---

## Support

- **Documentation:** https://docs.authsec.dev
- **Issues:** https://github.com/authsec-ai/authz-sdk/issues
- **Email:** support@authsec.dev

---

## License

MIT License - see [LICENSE](LICENSE) for details.
