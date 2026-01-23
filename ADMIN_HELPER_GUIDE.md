# Admin Helper SDK Guide

Complete guide for using `AdminHelper` to manage RBAC resources (roles, permissions, bindings, scopes).

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [SDK Initialization](#sdk-initialization)
5. [Role Management](#role-management)
6. [Permission Management](#permission-management)
7. [Role Binding Management](#role-binding-management)
8. [Scope Management](#scope-management)
9. [Secret Management](#secret-management)
10. [Endpoint Types](#endpoint-types)
11. [Advanced Usage](#advanced-usage)
12. [Error Handling](#error-handling)
13. [API Reference](#api-reference)
14. [Complete Examples](#complete-examples)

---

## Overview

### What is `AdminHelper`?

`AdminHelper` is the administrative SDK for managing Role-Based Access Control (RBAC) resources in your AuthSec deployment. It provides comprehensive tools for:

- **Role Management**: Create, update, list, and delete roles
- **Permission Management**: Create and manage fine-grained permissions
- **Role Bindings**: Assign roles to users with optional scoping
- **Scope Management**: Create and manage resource scopes
- **Secret Management**: Create and manage application secrets

### Who Should Use This?

- **System Administrators** managing user access and permissions
- **DevOps Teams** automating RBAC setup and configuration
- **Backend Engineers** integrating RBAC management into admin panels
- **Security Teams** implementing and auditing access control policies

### AdminHelper vs AuthSecClient

| Feature | AdminHelper | AuthSecClient |
|---------|-------------|---------------|
| **Purpose** | RBAC administration | User authentication |
| **Target Users** | Admins, DevOps | Application developers |
| **Operations** | Create/manage roles, permissions, bindings | Login, check permissions |
| **Database Access** | Admin or tenant DB | Tenant DB |
| **Requires** | Admin token | User credentials |

---

## Installation

```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

**Requirements:**
- Python 3.7 or higher
- `requests` library (auto-installed)

---

## Environment Setup

Set these environment variables (get from https://dashboard.authsec.dev):

```bash
export AUTHSEC_API_URL="https://api.authsec.dev"
export AUTHSEC_ADMIN_TOKEN="your-admin-token"
export AUTHSEC_TENANT_ID="your-tenant-id"
```

Or in Python:

```python
import os
os.environ['AUTHSEC_API_URL'] = 'https://api.authsec.dev'
os.environ['AUTHSEC_ADMIN_TOKEN'] = 'your-admin-token'
os.environ['AUTHSEC_TENANT_ID'] = 'your-tenant-id'
```

---

## Quick Start

```python
from authsec import AdminHelper
import os

# 1. Initialize with admin token
admin = AdminHelper(
    token=os.getenv('AUTHSEC_ADMIN_TOKEN'),
    endpoint_type="admin"  # or "enduser" for tenant operations
)

# 2. Create a permission
permission = admin.create_permission(
    resource="document",
    action="read",
    description="Read documents"
)

# 3. Create a role with permissions
role = admin.create_role(
    name="Viewer",
    description="Can view documents",
    permission_strings=["document:read"]
)

# 4. Assign role to user
binding = admin.create_role_binding(
    user_id="user-uuid",
    role_id=role['id']
)
```

**That's it!** Continue reading for detailed RBAC management.

### Python Example

```python
from authsec import AdminHelper

# 1. Initialize with admin token
admin = AdminHelper(
    token="your-admin-token",
    endpoint_type="admin"  # or "enduser"
)

# 2. Create a permission
permission = admin.create_permission(
    resource="document",
    action="write",
    description="Write documents"
)

# 3. Create a role with permissions
role = admin.create_role(
    name="Document Editor",
    description="Can read and write documents",
    permission_strings=["document:read", "document:write"]
)

# 4. Assign role to user
binding = admin.create_role_binding(
    user_id="user-uuid-123",
    role_id=role['id']
)

print(f"✓ Created role '{role['name']}' and assigned to user")
```

---

## SDK Initialization

### Basic Initialization

**Python:**
```python
from authsec import AdminHelper

# Minimal initialization (uses enduser endpoints by default)
admin = AdminHelper(token="your-admin-token")

# Custom base URL
admin = AdminHelper(
    token="your-admin-token",
    base_url="https://api.authsec.dev"
)
```

### Advanced Configuration

**Python:**
```python
admin = AdminHelper(
    token="your-admin-token",
    base_url="https://api.authsec.dev",
    timeout=15,                    # Request timeout in seconds
    debug=True,                    # Enable debug logging
    endpoint_type="admin"          # Use admin endpoints
)
```

### Initialize from Environment Variables

**Python:**
```bash
# Set environment variables
export ADMIN_TOKEN="your-admin-token"
export ADMIN_BASE_URL="https://api.authsec.dev"
export ADMIN_TIMEOUT="10"
export ENDPOINT_TYPE="admin"
```

```python
from authsec import AdminHelper

# Load configuration from environment
admin = AdminHelper.from_env()

# With debug mode
admin = AdminHelper.from_env(debug=True)
```

**Supported Environment Variables:**
- `ADMIN_TOKEN` - Required: Authentication token
- `ADMIN_BASE_URL` - Optional: API base URL (default: https://dev.api.authsec.dev)
- `ADMIN_TIMEOUT` - Optional: Request timeout in seconds (default: 10)
- `ENDPOINT_TYPE` - Optional: "admin" or "enduser" (default: "enduser")

---

## Role Management

### Create a Role

**Python:**
```python
# Create role with permissions
role = admin.create_role(
    name="Document Editor",
    description="Can read, write, and update documents",
    permission_strings=[
        "document:read",
        "document:write",
        "document:update"
    ]
)

print(f"Created role: {role['id']}")
print(f"Permissions: {role['permissions_count']}")
```

**Response:**
```json
{
    "id": "role-uuid-123",
    "name": "Document Editor",
    "description": "Can read, write, and update documents",
    "permissions_count": 3,
    "created_at": "2024-01-20T10:30:00Z"
}
```

### List Roles

**Python:**
```python
# List all roles
all_roles = admin.list_roles()

# Filter by resource
document_roles = admin.list_roles(resource="document")

# Filter by user
user_roles = admin.list_roles(user_id="user-uuid-123")

# Display roles
for role in all_roles:
    print(f"{role['name']}: {role['permissions_count']} permissions")
```

### Get Role Details

**Python:**
```python
role = admin.get_role("role-uuid-123")

print(f"Name: {role['name']}")
print(f"Description: {role['description']}")
print(f"Permissions:")
for perm in role.get('permissions', []):
    print(f"  - {perm['resource']}:{perm['action']}")
```

### Update a Role

**Python:**
```python
# Update role permissions
updated_role = admin.update_role(
    role_id="role-uuid-123",
    permission_strings=[
        "document:read",
        "document:write",
        "document:update",
        "document:delete"  # Added delete permission
    ]
)

print(f"Role now has {updated_role['permissions_count']} permissions")
```

### Delete a Role

**Python:**
```python
success = admin.delete_role("role-uuid-123")

if success:
    print("✓ Role deleted successfully")
else:
    print("✗ Failed to delete role")
```

---

## Permission Management

### Understanding Permissions

Permissions define what actions can be performed on resources:
- Format: `resource:action`
- Examples: `document:read`, `invoice:create`, `user:delete`

### Create a Permission

**Python:**
```python
# Create permission
permission = admin.create_permission(
    resource="invoice",
    action="create",
    description="Create new invoices"
)

print(f"Created permission: {permission['id']}")
```

**Response:**
```json
{
    "id": "perm-uuid-456",
    "resource": "invoice",
    "action": "create",
    "description": "Create new invoices",
    "created_at": "2024-01-20T10:35:00Z"
}
```

### List Permissions

**Python:**
```python
# List all permissions
all_perms = admin.list_permissions()

# Filter by resource
doc_perms = admin.list_permissions(resource="document")

# Display permissions
for perm in all_perms:
    print(f"{perm['resource']}:{perm['action']} - {perm.get('description', 'N/A')}")
```

**Example Output:**
```
document:read - Read documents
document:write - Write/create documents
document:update - Update existing documents
document:delete - Delete documents
invoice:read - Read invoices
invoice:create - Create invoices
```

### Batch Create Permissions

**Python:**
```python
# Create multiple permissions for a resource
resources = {
    "document": ["read", "write", "update", "delete"],
    "invoice": ["read", "create", "update", "delete", "approve"],
    "user": ["read", "create", "update", "delete", "admin"]
}

created_perms = []
for resource, actions in resources.items():
    for action in actions:
        try:
            perm = admin.create_permission(
                resource=resource,
                action=action,
                description=f"{action.capitalize()} {resource}"
            )
            created_perms.append(perm)
            print(f"✓ Created: {resource}:{action}")
        except Exception as e:
            print(f"✗ Failed to create {resource}:{action}: {e}")

print(f"\nTotal created: {len(created_perms)} permissions")
```

---

## Role Binding Management

### Understanding Role Bindings

Role bindings assign roles to users. They can be:
- **Tenant-wide**: User has the role across the entire tenant
- **Scoped**: User has the role only within a specific scope (project, organization, etc.)
- **Conditional**: Role active only when certain conditions are met

### Create a Role Binding (Tenant-wide)

**Python:**
```python
# Assign role to user (tenant-wide)
binding = admin.create_role_binding(
    user_id="user-uuid-123",
    role_id="editor-role-uuid"
)

print(f"Binding ID: {binding['id']}")
print(f"Status: {binding['status']}")
```

**Response:**
```json
{
    "id": "binding-uuid-789",
    "user_id": "user-uuid-123",
    "role_id": "editor-role-uuid",
    "status": "active",
    "scope_description": "Tenant-wide",
    "created_at": "2024-01-20T10:40:00Z"
}
```

### Create a Scoped Role Binding

**Python:**
```python
# Assign role scoped to a project
binding = admin.create_role_binding(
    user_id="user-uuid-123",
    role_id="project-admin-uuid",
    scope_type="project",
    scope_id="project-456"
)

print(f"✓ User is project admin for project-456")

# Assign role scoped to an organization
org_binding = admin.create_role_binding(
    user_id="user-uuid-123",
    role_id="org-manager-uuid",
    scope_type="organization",
    scope_id="org-789"
)
```

### Create a Conditional Role Binding

**Python:**
```python
# Role active only with MFA
mfa_binding = admin.create_role_binding(
    user_id="user-uuid-123",
    role_id="admin-role-uuid",
    conditions={"mfa_required": True}
)

# Time-based role
temp_binding = admin.create_role_binding(
    user_id="user-uuid-123",
    role_id="temp-access-uuid",
    conditions={
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_until": "2024-12-31T23:59:59Z"
    }
)

# Environment-based role
env_binding = admin.create_role_binding(
    user_id="user-uuid-123",
    role_id="dev-role-uuid",
    conditions={"environment": "development"}
)
```

### List Role Bindings

**Python:**
```python
# List all bindings
all_bindings = admin.list_role_bindings()

# List bindings for a specific user
user_bindings = admin.list_role_bindings(user_id="user-uuid-123")

# List bindings for a specific role
role_bindings = admin.list_role_bindings(role_id="editor-role-uuid")

# Display bindings
for binding in user_bindings:
    print(f"Role: {binding['role_id']}")
    print(f"  Scope: {binding.get('scope_description', 'Tenant-wide')}")
    print(f"  Status: {binding['status']}")
    print(f"  Created: {binding.get('created_at', 'N/A')}")
    print("---")
```

### Remove a Role Binding

**Python:**
```python
# Remove specific binding
success = admin.remove_role_binding("binding-uuid-789")

if success:
    print("✓ Role binding removed")
else:
    print("✗ Failed to remove binding")
```

### Bulk Remove Bindings

**Python:**
```python
# Remove all bindings for a user
user_bindings = admin.list_role_bindings(user_id="user-uuid-123")

removed_count = 0
for binding in user_bindings:
    try:
        admin.remove_role_binding(binding['id'])
        removed_count += 1
        print(f"✓ Removed binding {binding['id']}")
    except Exception as e:
        print(f"✗ Failed to remove {binding['id']}: {e}")

print(f"\nRemoved {removed_count}/{len(user_bindings)} bindings")
```

---

## Scope Management

### Understanding Scopes

Scopes define API or OAuth access boundaries:
- **OAuth Scopes**: Define what APIs can be accessed (e.g., `api.documents.read`)
- **Resource Scopes**: Group related resources together

### Create a Scope

**Python:**
```python
# Create API scope
scope = admin.create_scope(
    name="api.documents.write",
    description="Write access to documents API",
    resources=["document"]
)

print(f"Created scope: {scope['name']}")

# Create multi-resource scope
admin_scope = admin.create_scope(
    name="api.admin.full",
    description="Full admin API access",
    resources=["user", "role", "permission", "document", "invoice"]
)
```

**Response:**
```json
{
    "id": "scope-uuid-101",
    "name": "api.documents.write",
    "description": "Write access to documents API",
    "resources": ["document"],
    "created_at": "2024-01-20T10:45:00Z"
}
```

### List Scopes

**Python:**
```python
# List all scopes
scopes = admin.list_scopes()

for scope in scopes:
    print(f"{scope['name']}")
    print(f"  Description: {scope.get('description', 'N/A')}")
    print(f"  Resources: {', '.join(scope.get('resources', []))}")
```

### Common Scope Patterns

**Python:**
```python
# Read-only scopes
admin.create_scope(
    "api.read",
    "Read-only access to all APIs",
    ["document", "invoice", "user"]
)

# Resource-specific scopes
admin.create_scope(
    "api.documents.read",
    "Read documents",
    ["document"]
)

admin.create_scope(
    "api.documents.write",
    "Write documents",
    ["document"]
)

# Admin scopes
admin.create_scope(
    "api.admin",
    "Administrative access",
    ["user", "role", "permission"]
)
```

---

## Secret Management

### Create a Secret

**Python:**
```python
# Create secret
secret = admin.create_secret(
    name="api_key",
    value="sk-1234567890abcdef",
    metadata={"environment": "production", "team": "backend"}
)

print(f"Created secret: {secret['name']}")
```

**Response:**
```json
{
    "id": "secret-uuid-202",
    "name": "api_key",
    "metadata": {
        "environment": "production",
        "team": "backend"
    },
    "created_at": "2024-01-20T10:50:00Z"
}
```

**Note:** The secret `value` is NOT returned for security reasons.

### List Secrets

**Python:**
```python
# List all secrets
secrets = admin.list_secrets()

for secret in secrets:
    print(f"Name: {secret['name']}")
    print(f"  Metadata: {secret.get('metadata', {})}")
    print(f"  Created: {secret.get('created_at', 'N/A')}")
```

**Security Note:** Secret values are never returned in list operations. This prevents accidental exposure.

---

## Endpoint Types

### Admin vs EndUser Endpoints

The SDK supports two endpoint types, targeting different databases:

#### EndUser Endpoints (Default)

- **Endpoint Prefix**: `/uflow/enduser/*`
- **Database**: Tenant-specific database
- **Use Case**: Tenant-scoped RBAC management
- **Typical User**: Tenant administrators

**Python:**
```python
# Default: uses enduser endpoints
admin = AdminHelper(
    token="tenant-admin-token",
    endpoint_type="enduser"  # default
)
```

#### Admin Endpoints

- **Endpoint Prefix**: `/uflow/admin/*`
- **Database**: Primary admin database
- **Use Case**: Platform-level RBAC management
- **Typical User**: System administrators

**Python:**
```python
# Use admin endpoints
admin = AdminHelper(
    token="system-admin-token",
    endpoint_type="admin"
)
```

### Choosing the Right Endpoint Type

| Scenario | Endpoint Type |
|----------|---------------|
| Managing roles for your tenant | `enduser` |
| Managing roles across all tenants | `admin` |
| Creating permissions for your app | `enduser` |
| Creating system-wide permissions | `admin` |
| Assigning roles to your users | `enduser` |
| Managing platform-level access | `admin` |

### Switching Endpoint Types

**Python:**
```python
# Create separate instances for different operations
tenant_admin = AdminHelper(
    token="tenant-token",
    endpoint_type="enduser"
)

system_admin = AdminHelper(
    token="system-token",
    endpoint_type="admin"
)

# Tenant operations
tenant_role = tenant_admin.create_role("Tenant Editor", ["doc:write"])

# System operations
system_role = system_admin.create_role("System Admin", ["*:*"])
```

---

## Advanced Usage

### Complete RBAC Setup Workflow

**Python:**
```python
from authsec import AdminHelper

# Initialize
admin = AdminHelper(token="admin-token", endpoint_type="admin")

# Step 1: Create permissions
print("Creating permissions...")
permissions = {
    "document": ["read", "write", "update", "delete"],
    "invoice": ["read", "create", "approve", "delete"],
    "user": ["read", "create", "update", "delete"]
}

created_perms = []
for resource, actions in permissions.items():
    for action in actions:
        perm = admin.create_permission(resource, action)
        created_perms.append(perm)

print(f"✓ Created {len(created_perms)} permissions")

# Step 2: Create roles
print("\nCreating roles...")
roles = {
    "Viewer": ["document:read", "invoice:read", "user:read"],
    "Editor": ["document:read", "document:write", "document:update", "invoice:read"],
    "Admin": ["document:*", "invoice:*", "user:*"]  # All permissions
}

created_roles = {}
for role_name, perms in roles.items():
    role = admin.create_role(
        name=role_name,
        description=f"{role_name} role with specific permissions",
        permission_strings=perms
    )
    created_roles[role_name] = role

print(f"✓ Created {len(created_roles)} roles")

# Step 3: Create scopes
print("\nCreating scopes...")
scopes = {
    "api.read": (["document", "invoice", "user"], "Read-only API access"),
    "api.write": (["document", "invoice"], "Write API access"),
    "api.admin": (["user", "role", "permission"], "Admin API access")
}

for scope_name, (resources, description) in scopes.items():
    admin.create_scope(scope_name, description, resources)

print(f"✓ Created {len(scopes)} scopes")

# Step 4: Assign roles to users
print("\nAssigning roles...")
user_assignments = [
    ("user-1", "Viewer", None, None),
    ("user-2", "Editor", "project", "project-A"),
    ("user-3", "Admin", None, None)
]

for user_id, role_name, scope_type, scope_id in user_assignments:
    binding = admin.create_role_binding(
        user_id=user_id,
        role_id=created_roles[role_name]['id'],
        scope_type=scope_type,
        scope_id=scope_id
    )
    scope_desc = f"in {scope_id}" if scope_id else "tenant-wide"
    print(f"  ✓ {user_id}: {role_name} {scope_desc}")

print("\n✓ RBAC setup complete!")
```

### Audit and Reporting

**Python:**
```python
from authsec import AdminHelper
from collections import defaultdict

admin = AdminHelper.from_env()

# Generate RBAC audit report
print("=== RBAC Audit Report ===\n")

# 1. Count permissions by resource
print("Permissions by Resource:")
permissions = admin.list_permissions()
perm_counts = defaultdict(int)
for perm in permissions:
    perm_counts[perm['resource']] += 1

for resource, count in sorted(perm_counts.items()):
    print(f"  {resource}: {count} permissions")

# 2. Count roles and their permissions
print("\nRoles:")
roles = admin.list_roles()
for role in roles:
    print(f"  {role['name']}: {role['permissions_count']} permissions")

# 3. User role assignments
print("\nRole Bindings:")
bindings = admin.list_role_bindings()
user_bindings = defaultdict(list)
for binding in bindings:
    user_bindings[binding['user_id']].append(binding)

for user_id, user_binding_list in user_bindings.items():
    print(f"  User {user_id}: {len(user_binding_list)} role(s)")
    for binding in user_binding_list:
        scope = binding.get('scope_description', 'Tenant-wide')
        print(f"    - Role: {binding['role_id']} ({scope})")

# 4. Scopes
print("\nScopes:")
scopes = admin.list_scopes()
for scope in scopes:
    print(f"  {scope['name']}: {len(scope.get('resources', []))} resources")

print(f"\n=== Summary ===")
print(f"Total Permissions: {len(permissions)}")
print(f"Total Roles: {len(roles)}")
print(f"Total Bindings: {len(bindings)}")
print(f"Total Scopes: {len(scopes)}")
print(f"Unique Users: {len(user_bindings)}")
```

### Role Cleanup

**Python:**
```python
# Remove all inactive bindings
bindings = admin.list_role_bindings()
inactive_count = 0

for binding in bindings:
    if binding['status'] == 'inactive':
        admin.remove_role_binding(binding['id'])
        inactive_count += 1

print(f"✓ Removed {inactive_count} inactive bindings")

# Remove roles with no bindings
all_roles = admin.list_roles()
removed_roles = 0

for role in all_roles:
    role_bindings = admin.list_role_bindings(role_id=role['id'])
    if len(role_bindings) == 0:
        admin.delete_role(role['id'])
        removed_roles += 1
        print(f"  Deleted unused role: {role['name']}")

print(f"✓ Removed {removed_roles} unused roles")
```

### Migration Script

**Python:**
```python
"""
Migrate RBAC configuration from one environment to another
"""
from authsec import AdminHelper
import json

# Source environment
source = AdminHelper(
    token="source-admin-token",
    base_url="https://dev.api.authsec.dev",
    endpoint_type="admin"
)

# Target environment
target = AdminHelper(
    token="target-admin-token",
    base_url="https://prod.api.authsec.dev",
    endpoint_type="admin"
)

# Export from source
print("Exporting from source...")
export_data = {
    "permissions": source.list_permissions(),
    "roles": source.list_roles(),
    "scopes": source.list_scopes()
}

# Save to file
with open("rbac_export.json", "w") as f:
    json.dump(export_data, f, indent=2)

print(f"✓ Exported {len(export_data['permissions'])} permissions")
print(f"✓ Exported {len(export_data['roles'])} roles")
print(f"✓ Exported {len(export_data['scopes'])} scopes")

# Import to target
print("\nImporting to target...")

# Import permissions
for perm in export_data['permissions']:
    try:
        target.create_permission(
            perm['resource'],
            perm['action'],
            perm.get('description')
        )
    except Exception as e:
        print(f"  ⚠ Permission {perm['resource']}:{perm['action']} exists")

# Import scopes
for scope in export_data['scopes']:
    try:
        target.create_scope(
            scope['name'],
            scope.get('description'),
            scope.get('resources', [])
        )
    except Exception as e:
        print(f"  ⚠ Scope {scope['name']} exists")

# Import roles
for role in export_data['roles']:
    try:
        target.create_role(
            role['name'],
            role.get('description'),
            role.get('permission_strings', [])
        )
    except Exception as e:
        print(f"  ⚠ Role {role['name']} exists")

print("\n✓ Migration complete!")
```

---

## Error Handling

### Exception Types

**Python:**
```python
from authsec.admin_helper import (
    AdminSDKError,        # Base exception
    PermissionError,      # Permission operations
    RoleBindingError,     # Role binding operations
    ScopeError,           # Scope operations
    SecretError           # Secret operations
)
```

### Basic Error Handling

**Python:**
```python
from authsec import AdminHelper
from authsec.admin_helper import AdminSDKError

admin = AdminHelper(token="admin-token")

try:
    role = admin.create_role("Test Role", ["doc:read"])
except AdminSDKError as e:
    print(f"SDK error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Specific Error Handling

**Python:**
```python
from authsec.admin_helper import PermissionError, RoleBindingError, ScopeError

# Handle permission errors
try:
    perm = admin.create_permission("document", "read")
except PermissionError as e:
    print(f"Permission creation failed: {e}")
    # Handle duplicate permission gracefully

# Handle binding errors
try:
    binding = admin.create_role_binding(
        user_id="invalid-user",
        role_id="invalid-role"
    )
except RoleBindingError as e:
    print(f"Binding creation failed: {e}")
    # User or role doesn't exist

# Handle scope errors
try:
    scope = admin.create_scope("invalid..name")
except ScopeError as e:
    print(f"Invalid scope name: {e}")
```

### Retry Logic

**Python:**
```python
import time
from authsec import AdminHelper
from authsec.admin_helper import AdminSDKError

def create_role_with_retry(admin, name, perms, max_retries=3):
    """Create role with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            return admin.create_role(name, perms)
        except AdminSDKError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise  # Re-raise after max retries

# Usage
admin = AdminHelper.from_env()
role = create_role_with_retry(admin, "Test Role", ["doc:read"])
```

### Graceful Degradation

**Python:**
```python
def safe_create_permission(admin, resource, action, description=None):
    """Create permission with fallback"""
    try:
        return admin.create_permission(resource, action, description)
    except Exception as e:
        print(f"⚠ Failed to create {resource}:{action}: {e}")
        # Return None or default value
        return None

# Usage
perms = []
for resource in ["doc", "invoice", "user"]:
    for action in ["read", "write"]:
        perm = safe_create_permission(admin, resource, action)
        if perm:
            perms.append(perm)

print(f"Created {len(perms)} permissions (some may have failed)")
```

---

## API Reference

### Constructor

**Python:**
```python
AdminHelper(
    token: str,
    base_url: str = "https://dev.api.authsec.dev",
    timeout: int = 10,
    debug: bool = False,
    endpoint_type: str = "enduser"
)
```

**Class Method:**
```python
AdminHelper.from_env(debug: bool = False) -> AdminHelper
```

### Role Management Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_role()` | `name`, `description?`, `permission_strings?` | `dict` | Create a new role |
| `list_roles()` | `resource?`, `user_id?` | `list` | List roles with filters |
| `get_role()` | `role_id` | `dict` | Get role details |
| `update_role()` | `role_id`, `permission_strings` | `dict` | Update role permissions |
| `delete_role()` | `role_id` | `bool` | Delete a role |

### Permission Management Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_permission()` | `resource`, `action`, `description?` | `dict` | Create a permission |
| `list_permissions()` | `resource?` | `list` | List permissions |

### Role Binding Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_role_binding()` | `user_id`, `role_id`, `scope_type?`, `scope_id?`, `conditions?` | `dict` | Create role binding |
| `list_role_bindings()` | `user_id?`, `role_id?` | `list` | List role bindings |
| `remove_role_binding()` | `binding_id` | `bool` | Remove role binding |

### Scope Management Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_scope()` | `name`, `description?`, `resources?` | `dict` | Create a scope |
| `list_scopes()` | - | `list` | List all scopes |

### Secret Management Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_secret()` | `name`, `value`, `metadata?` | `dict` | Create a secret |
| `list_secrets()` | - | `list` | List all secrets |

---

## Complete Examples

### Example 1: Multi-Tenant RBAC Setup

**Python:**
```python
from authsec import AdminHelper

# Initialize for tenant
admin = AdminHelper(
    token="tenant-admin-token",
    endpoint_type="enduser"
)

# Define tenant structure
projects = ["Project Alpha", "Project Beta", "Project Gamma"]
teams = ["Engineering", "Design", "Marketing"]

# Create project-specific roles
for project in projects:
    # Viewer role for project
    viewer = admin.create_role(
        name=f"{project} Viewer",
        description=f"Read-only access to {project}",
        permission_strings=["document:read", "task:read"]
    )
    
    # Editor role for project
    editor = admin.create_role(
        name=f"{project} Editor",
        description=f"Edit access to {project}",
        permission_strings=["document:read", "document:write", "task:read", "task:write"]
    )
    
    print(f"✓ Created roles for {project}")

# Create team roles
team_permissions = {
    "Engineering": ["code:read", "code:write", "deploy:execute"],
    "Design": ["design:read", "design:write", "asset:manage"],
    "Marketing": ["content:read", "content:write", "analytics:view"]
}

for team, perms in team_permissions.items():
    role = admin.create_role(
        name=f"{team} Team",
        description=f"Standard permissions for {team} team",
        permission_strings=perms
    )
    print(f"✓ Created role for {team} team")

print("\n✓ Multi-tenant RBAC setup complete!")
```

### Example 2: Temporary Access Grant

**Python:**
```python
from authsec import AdminHelper
from datetime import datetime, timedelta

admin = AdminHelper.from_env()

# Grant temporary admin access (7 days)
expires_at = datetime.utcnow() + timedelta(days=7)

temp_binding = admin.create_role_binding(
    user_id="contractor-user-uuid",
    role_id="admin-role-uuid",
    conditions={
        "valid_until": expires_at.isoformat() + "Z",
        "reason": "Q1 migration project"
    }
)

print(f"✓ Temporary admin access granted")
print(f"  User: contractor-user-uuid")
print(f"  Expires: {expires_at.strftime('%Y-%m-%d %H:%M')}")
print(f"  Binding ID: {temp_binding['id']}")
```

### Example 3: Permission Audit

**Python:**
```python
from authsec import AdminHelper
from collections import defaultdict

admin = AdminHelper.from_env()

print("=== Permission Audit ===\n")

# Get all users' role bindings
all_bindings = admin.list_role_bindings()

# Group by user
user_access = defaultdict(lambda: {"roles": [], "scopes": []})

for binding in all_bindings:
    user_id = binding['user_id']
    user_access[user_id]['roles'].append(binding['role_id'])
    user_access[user_id]['scopes'].append(
        binding.get('scope_description', 'Tenant-wide')
    )

# Report
print(f"Total users with access: {len(user_access)}")
print(f"Total role bindings: {len(all_bindings)}\n")

for user_id, access in user_access.items():
    print(f"User: {user_id}")
    print(f"  Roles: {len(access['roles'])}")
    for i, (role, scope) in enumerate(zip(access['roles'], access['scopes']), 1):
        print(f"    {i}. {role} ({scope})")
    print()

# Find users with multiple roles
multi_role_users = [
    (user, len(access['roles'])) 
    for user, access in user_access.items() 
    if len(access['roles']) > 1
]

print(f"Users with multiple roles: {len(multi_role_users)}")
for user, count in sorted(multi_role_users, key=lambda x: x[1], reverse=True):
    print(f"  {user}: {count} roles")
```

### Example 4: Bulk User Onboarding

**Python:**
```python
from authsec import AdminHelper
import csv

admin = AdminHelper(token="admin-token", endpoint_type="enduser")

# Read users from CSV
# Format: user_id, role_name, scope_type, scope_id
with open('new_users.csv', 'r') as f:
    reader = csv.DictReader(f)
    users = list(reader)

# Get all roles first (to map names to IDs)
all_roles = admin.list_roles()
role_map = {role['name']: role['id'] for role in all_roles}

# Process each user
success_count = 0
failed_count = 0

for user in users:
    user_id = user['user_id']
    role_name = user['role_name']
    scope_type = user.get('scope_type') or None
    scope_id = user.get('scope_id') or None
    
    # Get role ID
    role_id = role_map.get(role_name)
    if not role_id:
        print(f"✗ Role '{role_name}' not found for user {user_id}")
        failed_count += 1
        continue
    
    # Create binding
    try:
        binding = admin.create_role_binding(
            user_id=user_id,
            role_id=role_id,
            scope_type=scope_type,
            scope_id=scope_id
        )
        success_count += 1
        scope_desc = f" in {scope_id}" if scope_id else ""
        print(f"✓ {user_id}: {role_name}{scope_desc}")
    except Exception as e:
        failed_count += 1
        print(f"✗ Failed for {user_id}: {e}")

print(f"\n=== Summary ===")
print(f"Total users: {len(users)}")
print(f"Successful: {success_count}")
print(f"Failed: {failed_count}")
```

---

## Testing and Troubleshooting

### Testing Your Setup

**Python:**
```python
from authsec import AdminHelper

def test_admin_setup():
    """Test admin SDK configuration"""
    admin = AdminHelper.from_env(debug=True)
    
    # Test 1: List permissions
    print("Test 1: List permissions...")
    perms = admin.list_permissions()
    print(f"✓ Found {len(perms)} permissions")
    
    # Test 2: List roles
    print("\nTest 2: List roles...")
    roles = admin.list_roles()
    print(f"✓ Found {len(roles)} roles")
    
    # Test 3: List bindings
    print("\nTest 3: List bindings...")
    bindings = admin.list_role_bindings()
    print(f"✓ Found {len(bindings)} bindings")
    
    # Test 4: List scopes
    print("\nTest 4: List scopes...")
    scopes = admin.list_scopes()
    print(f"✓ Found {len(scopes)} scopes")
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_admin_setup()
```

### Debug Mode

**Python:**
```python
# Enable debug logging to see all API requests
admin = AdminHelper(
    token="admin-token",
    debug=True
)

# All requests will now log:
# - Request method and URL
# - Request body
# - Response status
# - Response body (first 500 chars)
```

---

## Need More Help?

- **User Authentication**: See [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)
- **API Documentation**: https://docs.authsec.dev
- **Interactive API Docs**: https://dev.api.authsec.dev/uflow/redoc
- **Support**: support@authsec.dev
- **GitHub Issues**: [Repository Issues](https://github.com/authsec-ai/authsec-python-sdk/issues)
