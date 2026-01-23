# Authentication & Authorization SDK Guide

Complete guide for using `AuthSecClient` to add authentication and authorization to your applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [SDK Initialization](#sdk-initialization)
5. [Authentication](#authentication)
6. [Authorization & Permission Checking](#authorization--permission-checking)
7. [Role Management](#role-management)
8. [Advanced Usage](#advanced-usage)
9. [Error Handling](#error-handling)
10. [API Reference](#api-reference)
11. [Complete Examples](#complete-examples)

---

## Overview

### What is `AuthSecClient`?

`AuthSecClient` is the primary SDK for integrating authentication and authorization into your applications. It provides:

- **Token Management**: Generate, verify, and manage JWT tokens
- **User Authentication**: OIDC integration, token generation
- **Permission Checking**: Validate user permissions for resources and actions
- **Role Assignment**: Assign roles to users in your application
- **Authenticated Requests**: Automatically inject tokens in API calls

### Who Should Use This?

- **Application Developers** building apps that need authentication
- **Backend Engineers** implementing authorization logic
- **Frontend Developers** managing user sessions and permissions

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
export AUTHSEC_CLIENT_ID="your-client-id"
export AUTHSEC_TENANT_ID="your-tenant-id"
```

Or in Python:

```python
import os
os.environ['AUTHSEC_API_URL'] = 'https://api.authsec.dev'
os.environ['AUTHSEC_CLIENT_ID'] = 'your-client-id'
os.environ['AUTHSEC_TENANT_ID'] = 'your-tenant-id'
```

---

## Quick Start

```python
from authsec import AuthSecClient
import os

# 1. Initialize client
client = AuthSecClient(os.getenv('AUTHSEC_API_URL'))

# 2. Login with user credentials
token = client.login(
    email="user@example.com",
    password="user-password",
    client_id=os.getenv('AUTHSEC_CLIENT_ID')
)

# 3. Check permissions
if client.check_permission("document", "read"):
    print("✓ User can read documents")
else:
    print("✗ Access denied")
```

**That's it!** Continue reading for detailed usage.

# 3. Check permissions
if client.check_permission("document", "read"):
    print("✓ User can read documents")
else:
    print("✗ Permission denied")

# 4. Check scoped permission
if client.check_permission_scoped("document", "write", "project", "project-123"):
    print("✓ User can write documents in this project")
```

### TypeScript Example

```typescript
import { AuthSecClient } from '@authsec/sdk';

// 1. Initialize client
const client = new AuthSecClient('https://api.authsec.dev');

// 2. Set authentication token (from OIDC or other source)
client.setToken('your-jwt-token');

// 3. Check permission
const canRead = await client.checkPermission('document', 'read');
console.log(canRead ? '✓ Can read' : '✗ Cannot read');
```

---

## SDK Initialization

### Basic Initialization

**Python:**
```python
from authsec import AuthSecClient

client = AuthSecClient("https://api.authsec.dev")
```

**TypeScript:**
```typescript
import { AuthSecClient } from '@authsec/sdk';

const client = new AuthSecClient('https://api.authsec.dev');
```

### Advanced Configuration

**Python:**
```python
client = AuthSecClient(
    base_url="https://api.authsec.dev",
    timeout=10.0,                          # Request timeout in seconds
    legacy_proxy_mode=False,               # Use legacy endpoints
    uflow_base_url=None,                   # Separate user-flow URL
    token="existing-token-if-available"    # Pre-authenticated token
)
```

**TypeScript:**
```typescript
const client = new AuthSecClient(
    'https://api.authsec.dev',
    10000,                                 // Timeout in milliseconds
    'existing-token-if-available'          // Pre-authenticated token
);
```

### Split Architecture (Advanced)

If your auth-manager and user-flow services are on different hosts:

**Python:**
```python
client = AuthSecClient(
    base_url="http://localhost:7469",              # Auth-manager
    uflow_base_url="https://api.authsec.dev"      # User-flow service
)
```

### Using Pre-Authenticated Tokens

If you already have a token (e.g., from OIDC or other authentication):

**Python:**
```python
# Option 1: During initialization
client = AuthSecClient(
    base_url="https://api.authsec.dev",
    token="eyJhbGc..."
)

# Option 2: Set token later
client = AuthSecClient("https://api.authsec.dev")
client.set_token("eyJhbGc...")
```

**TypeScript:**
```typescript
// During initialization
const client = new AuthSecClient(
    'https://api.authsec.dev',
    undefined,
    'eyJhbGc...'
);

// Set token later
client.setToken('eyJhbGc...');
```

### Environment-Based Configuration

**Python:**
```bash
export AUTH_BASE_URL="https://api.authsec.dev"
export AUTH_TIMEOUT="10"
```

```python
import os
from authsec import AuthSecClient

client = AuthSecClient(
    base_url=os.getenv("AUTH_BASE_URL", "https://api.authsec.dev"),
    timeout=float(os.getenv("AUTH_TIMEOUT", "5.0"))
)
```

---

## Authentication

### Method 1: OIDC Token Exchange

Exchange an OIDC token (from Google, Auth0, etc.) for an AuthSec token:

**Python:**
```python
# After user authenticates with OIDC provider
oidc_token = "token_from_google_or_auth0"

token = client.exchange_oidc(
    code=oidc_token,
    client_id="your-client-id"
)

# Token is now set and ready to use
```

**TypeScript:**
```typescript
const oidcToken = 'token_from_google_or_auth0';

const token = await client.exchangeOidc(
    oidcToken,
    'your-client-id'
);
```

### Method 2: Generate Token (Server-Side)

For server-to-server communication or testing:

**Python:**
```python
token = client.generate_token(
    tenant_id="tenant-uuid",
    project_id="project-uuid",
    client_id="client-uuid",
    email_id="user@example.com",
    secret_id=None  # Optional secret ID for enhanced security
)
```

**TypeScript:**
```typescript
const token = await client.generateToken({
    tenantId: 'tenant-uuid',
    projectId: 'project-uuid',
    clientId: 'client-uuid',
    emailId: 'user@example.com'
});
```

### Token Verification

Verify a token's validity:

**Python:**
```python
# Verify the current token
claims = client.verify_token()

# Verify a specific token
claims = client.verify_token("eyJhbGc...")

if claims:
    print(f"Token is valid for user: {claims.get('email_id')}")
else:
    print("Token is invalid or expired")
```

**TypeScript:**
```typescript
const claims = await client.verifyToken();

if (claims) {
    console.log(`Token valid for: ${claims.email_id}`);
} else {
    console.log('Token invalid');
}
```

### Managing Tokens

**Python:**
```python
# Set token manually
client.set_token("eyJhbGc...")

# Get current token
current_token = client.token

# Check if token is set
if client.token:
    print("Client is authenticated")
```

**TypeScript:**
```typescript
// Set token
client.setToken('eyJhbGc...');

// Get token
const token = client.getToken();
```

---

## Authorization & Permission Checking

### Understanding Permissions

Permissions in AuthSec follow the format: `resource:action`

**Examples:**
- `document:read` - Can read documents
- `document:write` - Can write/create documents
- `document:delete` - Can delete documents
- `invoice:create` - Can create invoices
- `user:admin` - Admin access to users

### Basic Permission Checking

Check if the authenticated user has a specific permission:

**Python:**
```python
# Check if user can read documents
if client.check_permission("document", "read"):
    # User has permission
    documents = fetch_documents()
else:
    # User lacks permission
    raise PermissionError("Cannot read documents")
```

**TypeScript:**
```typescript
const canRead = await client.checkPermission('document', 'read');

if (canRead) {
    const documents = await fetchDocuments();
} else {
    throw new Error('Permission denied');
}
```

### Scoped Permission Checking

Check permissions within a specific scope (tenant, project, organization):

**Python:**
```python
# Check if user can write documents in a specific project
can_write = client.check_permission_scoped(
    resource="document",
    action="write",
    scope_type="project",
    scope_id="project-uuid-123"
)

if can_write:
    update_document(doc_id)
```

**TypeScript:**
```typescript
const canWrite = await client.checkPermissionScoped(
    'document',
    'write',
    'project',
    'project-uuid-123'
);
```

**Scope Types:**
- `tenant` - Tenant-wide scope
- `project` - Project-specific scope
- `organization` - Organization-level scope
- Custom scope types (as configured in your system)

### List All User Permissions

Get all permissions for the authenticated user:

**Python:**
```python
permissions = client.list_permissions()

# Returns:
# [
#     {"resource": "document", "actions": ["read", "write"]},
#     {"resource": "invoice", "actions": ["read", "create", "delete"]},
#     {"resource": "user", "actions": ["read"]}
# ]

# Check what actions user can perform on documents
for perm in permissions:
    if perm["resource"] == "document":
        print(f"Document actions: {perm['actions']}")
```

**TypeScript:**
```typescript
const permissions = await client.listPermissions();

permissions.forEach(perm => {
    console.log(`${perm.resource}: ${perm.actions.join(', ')}`);
});
```

### Multiple Permission Checks

**Python:**
```python
# Check multiple permissions at once
required_perms = [
    ("document", "read"),
    ("document", "write"),
    ("invoice", "read")
]

# Check if user has ALL required permissions
has_all = all(
    client.check_permission(resource, action) 
    for resource, action in required_perms
)

# Check if user has ANY of the permissions
has_any = any(
    client.check_permission(resource, action) 
    for resource, action in required_perms
)
```

### Permission-Based Access Control Pattern

**Python:**
```python
from functools import wraps

def require_permission(resource: str, action: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not client.check_permission(resource, action):
                raise PermissionError(f"Missing permission: {resource}:{action}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_permission("invoice", "create")
def create_invoice(data):
    # Only executes if user has invoice:create permission
    return save_invoice(data)

@require_permission("document", "delete")
def delete_document(doc_id):
    # Only executes if user has document:delete permission
    return remove_document(doc_id)
```

**TypeScript:**
```typescript
function requirePermission(resource: string, action: string) {
    return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = async function (...args: any[]) {
            const hasPermission = await client.checkPermission(resource, action);
            if (!hasPermission) {
                throw new Error(`Missing permission: ${resource}:${action}`);
            }
            return originalMethod.apply(this, args);
        };
        
        return descriptor;
    };
}

// Usage
class DocumentService {
    @requirePermission('document', 'delete')
    async deleteDocument(docId: string) {
        // Only executes if user has document:delete permission
        return await removeDocument(docId);
    }
}
```

---

## Role Management

### Assign Role to User

**Python:**
```python
# Assign a role to a user (tenant-wide)
binding = client.assign_role(
    user_id="user-uuid-123",
    role_id="editor-role-uuid"
)

print(f"Created binding: {binding['id']}")
print(f"Status: {binding['status']}")
```

**TypeScript:**
```typescript
const binding = await client.assignRole(
    'user-uuid-123',
    'editor-role-uuid'
);

console.log(`Binding ID: ${binding.id}`);
```

### Scoped Role Assignment

Assign a role with specific scope:

**Python:**
```python
# Assign role scoped to a specific project
binding = client.assign_role(
    user_id="user-uuid",
    role_id="project-admin-role-uuid",
    scope_type="project",
    scope_id="project-uuid-456"
)

# User now has project-admin role only for project-456
```

**TypeScript:**
```typescript
const binding = await client.assignRole(
    'user-uuid',
    'project-admin-role-uuid',
    {
        scopeType: 'project',
        scopeId: 'project-uuid-456'
    }
);
```

### Conditional Role Assignment

Assign roles with conditions:

**Python:**
```python
# Role active only with MFA
binding = client.assign_role(
    user_id="user-uuid",
    role_id="admin-role-uuid",
    conditions={"mfa_required": True}
)

# Role with time-based condition
binding = client.assign_role(
    user_id="user-uuid",
    role_id="temp-role-uuid",
    conditions={
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_until": "2024-12-31T23:59:59Z"
    }
)
```

### List Role Bindings

**Python:**
```python
# List all bindings for a user
bindings = client.list_role_bindings(user_id="user-uuid")

for binding in bindings:
    print(f"Role: {binding['role_id']}")
    print(f"Scope: {binding.get('scope_description', 'Tenant-wide')}")
    print(f"Status: {binding['status']}")
    print("---")

# List all bindings (admin operation)
all_bindings = client.list_role_bindings(admin=True)
```

**TypeScript:**
```typescript
const bindings = await client.listRoleBindings({
    userId: 'user-uuid'
});

bindings.forEach(binding => {
    console.log(`Role: ${binding.role_id}, Status: ${binding.status}`);
});
```

### Remove Role Binding

**Python:**
```python
# Remove a specific role binding
success = client.remove_role_binding("binding-uuid-123")

if success:
    print("✓ Role binding removed")
else:
    print("✗ Failed to remove binding")
```

**TypeScript:**
```typescript
await client.removeRoleBinding('binding-uuid-123');
console.log('✓ Binding removed');
```

---

## Advanced Usage

### Making Authenticated API Requests

The SDK can automatically inject authentication tokens in your API requests:

**Python:**
```python
# The token is automatically included in the Authorization header
response = client.request(
    method="GET",
    url_or_path="/api/v1/documents",
    params={"status": "published"}
)

if response.status_code == 200:
    documents = response.json()
    print(f"Found {len(documents)} documents")

# POST request
response = client.request(
    method="POST",
    url_or_path="/api/v1/documents",
    json={"title": "New Document", "content": "..."}
)

# PUT request
response = client.request(
    method="PUT",
    url_or_path="/api/v1/documents/123",
    json={"title": "Updated Title"}
)

# DELETE request
response = client.request(
    method="DELETE",
    url_or_path="/api/v1/documents/123"
)
```

**TypeScript:**
```typescript
// GET request
const response = await client.request('GET', '/api/v1/documents', {
    params: { status: 'published' }
});

// POST request
const newDoc = await client.request('POST', '/api/v1/documents', {
    data: { title: 'New Document', content: '...' }
});
```

### Token Refresh Pattern

**Python:**
```python
import time

class AuthManager:
    def __init__(self, client: AuthSecClient):
        self.client = client
        self.token_expiry = None
    
    def ensure_valid_token(self):
        """Refresh token if expired"""
        if self.token_expiry and time.time() >= self.token_expiry:
            # Refresh logic - re-authenticate via OIDC or regenerate token
            # new_token = self.client.exchange_oidc(refresh_code, client_id)
            self.token_expiry = time.time() + 3600
        
    def make_request(self, *args, **kwargs):
        self.ensure_valid_token()
        return self.client.request(*args, **kwargs)
```

### Local vs Remote Permission Checking

**Python:**
```python
# Remote check (queries the API)
has_perm = client.check_permission("document", "read")

# Local check (from JWT claims) - faster but less fresh
import jwt

token_claims = jwt.decode(
    client.token, 
    options={"verify_signature": False}
)

# Check if permission exists in token
perms = token_claims.get("perms", [])
has_local_perm = any(
    p["r"] == "document" and "read" in p["a"] 
    for p in perms
)
```

### Caching Permissions

**Python:**
```python
from functools import lru_cache
from time import time

class CachedAuthClient:
    def __init__(self, client: AuthSecClient, cache_ttl=300):
        self.client = client
        self.cache_ttl = cache_ttl
        self._cache = {}
    
    def check_permission(self, resource: str, action: str) -> bool:
        cache_key = f"{resource}:{action}"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, result = self._cache[cache_key]
            if time() - cached_time < self.cache_ttl:
                return result
        
        # Query API
        result = self.client.check_permission(resource, action)
        
        # Update cache
        self._cache[cache_key] = (time(), result)
        
        return result
```

---

## Error Handling

### Basic Error Handling

**Python:**
```python
from authsec import AuthSecClient

client = AuthSecClient("https://api.authsec.dev")

try:
    token = client.exchange_oidc(
        code="oidc-authorization-code",
        client_id="client-id"
    )
except Exception as e:
    print(f"Token exchange failed: {e}")
    # Handle authentication failure

try:
    if client.check_permission("document", "read"):
        # Proceed with operation
        pass
except Exception as e:
    print(f"Permission check failed: {e}")
    # Handle API error
```

**TypeScript:**
```typescript
try {
    const token = await client.exchangeOidc(
        'oidc-authorization-code',
        'client-id'
    );
} catch (error) {
    console.error('Token exchange failed:', error);
    // Handle authentication failure
}
```

### HTTP Error Handling

**Python:**
```python
import requests

try:
    response = client.request("GET", "/api/v1/documents")
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    documents = response.json()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        print("Unauthorized - token may be expired")
    elif e.response.status_code == 403:
        print("Forbidden - insufficient permissions")
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print(f"HTTP error: {e}")
except requests.RequestException as e:
    print(f"Request failed: {e}")
```

### Graceful Degradation

**Python:**
```python
def safe_check_permission(resource: str, action: str) -> bool:
    """Check permission with fallback to deny"""
    try:
        return client.check_permission(resource, action)
    except Exception as e:
        # Log error
        print(f"Permission check failed: {e}")
        # Deny by default for security
        return False

# Usage
if safe_check_permission("document", "read"):
    # Proceed
    pass
```

---

## API Reference

### Constructor

**Python:**
```python
AuthSecClient(
    base_url: str,
    timeout: float = 5.0,
    legacy_proxy_mode: bool = False,
    uflow_base_url: Optional[str] = None,
    token: Optional[str] = None
)
```

**TypeScript:**
```typescript
new AuthSecClient(
    baseUrl: string,
    timeout?: number,
    token?: string
)
```

### Authentication Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `exchange_oidc()` | `code`, `client_id` | `str` (token) | Exchange OIDC token |
| `generate_token()` | `tenant_id`, `project_id`, `client_id`, `email_id`, `secret_id?` | `str` (token) | Generate JWT token |
| `verify_token()` | `token?` | `dict` (claims) or `None` | Verify token validity |
| `set_token()` | `token` | `None` | Set authentication token |

### Authorization Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `check_permission()` | `resource`, `action` | `bool` | Check if user has permission |
| `check_permission_scoped()` | `resource`, `action`, `scope_type`, `scope_id` | `bool` | Check scoped permission |
| `list_permissions()` | - | `list` | List all user permissions |

### Role Management Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `assign_role()` | `user_id`, `role_id`, `scope_type?`, `scope_id?`, `conditions?`, `admin?` | `dict` (binding) | Assign role to user |
| `list_role_bindings()` | `user_id?`, `admin?` | `list` | List role bindings |
| `remove_role_binding()` | `binding_id`, `admin?` | `bool` | Remove role binding |

### Request Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `request()` | `method`, `url_or_path`, `**kwargs` | `Response` | Make authenticated HTTP request |

---

## Complete Examples

### Example 1: Full Authentication Flow

**Python:**
```python
from authsec import AuthSecClient

# Initialize
client = AuthSecClient("https://api.authsec.dev")

# Authenticate with OIDC or get token from elsewhere
try:
    token = client.exchange_oidc(
        code="oidc-authorization-code",
        client_id="your-client-id"
    )
    print("✓ Token obtained successfully")
except Exception as e:
    print(f"✗ Token exchange failed: {e}")
    exit(1)

# Verify token
claims = client.verify_token()
if claims:
    print(f"✓ Token valid for: {claims.get('email_id')}")
    print(f"  Tenant: {claims.get('tenant_id')}")
    print(f"  Expires: {claims.get('exp')}")

# Check permissions
if client.check_permission("document", "read"):
    print("✓ Can read documents")
    
    # List all permissions
    permissions = client.list_permissions()
    print(f"\nUser has {len(permissions)} permission groups:")
    for perm in permissions:
        print(f"  {perm['resource']}: {', '.join(perm['actions'])}")

# Check scoped permission
if client.check_permission_scoped("document", "write", "project", "project-123"):
    print("✓ Can write documents in project-123")
else:
    print("✗ Cannot write documents in this project")
```

### Example 2: OIDC Integration

**Python:**
```python
from authsec import AuthSecClient

# After user authenticates with OIDC provider (Google, Auth0, etc.)
# You receive an authorization code

client = AuthSecClient("https://api.authsec.dev")

# Exchange OIDC code for AuthSec token
try:
    token = client.exchange_oidc(
        code="authorization_code_from_oidc_provider",
        client_id="your-client-id"
    )
    print("✓ OIDC token exchanged successfully")
    
    # Token is now set in client and ready to use
    if client.check_permission("user", "read"):
        print("✓ User has basic access")
        
except Exception as e:
    print(f"✗ OIDC exchange failed: {e}")
```

### Example 3: Role-Based Access in Web Application

**Python (Flask):**
```python
from flask import Flask, request, jsonify, abort
from authsec import AuthSecClient
from functools import wraps

app = Flask(__name__)
client = AuthSecClient("https://api.authsec.dev")

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, 'Missing or invalid token')
        
        token = auth_header.split(' ')[1]
        client.set_token(token)
        
        # Verify token
        claims = client.verify_token()
        if not claims:
            abort(401, 'Invalid or expired token')
        
        request.user_claims = claims
        return f(*args, **kwargs)
    return decorated

def require_permission(resource, action):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not client.check_permission(resource, action):
                abort(403, f'Missing permission: {resource}:{action}')
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/api/documents', methods=['GET'])
@require_token
@require_permission('document', 'read')
def get_documents():
    # User is authenticated and has permission
    return jsonify({"documents": [...]})

@app.route('/api/documents', methods=['POST'])
@require_token
@require_permission('document', 'create')
def create_document():
    # User can create documents
    data = request.json
    return jsonify({"id": "doc-123", "status": "created"})

@app.route('/api/documents/<doc_id>', methods=['DELETE'])
@require_token
@require_permission('document', 'delete')
def delete_document(doc_id):
    # User can delete documents
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    app.run()
```

### Example 4: Using Pre-Authenticated Token

**Python:**
```python
import os
from authsec import AuthSecClient

# Scenario: You already have a token from elsewhere
# (e.g., stored in environment variable, session, or cookie)

existing_token = os.getenv("USER_TOKEN")

# Initialize client with existing token
client = AuthSecClient(
    base_url="https://api.authsec.dev",
    token=existing_token
)

# No need to authenticate - token is already set
# Start using permission checks immediately
if client.check_permission("invoice", "read"):
    invoices = fetch_user_invoices()
    print(f"Fetched {len(invoices)} invoices")
```

### Example 5: Scoped Permissions in Multi-Tenant App

**Python:**
```python
from authsec import AuthSecClient

client = AuthSecClient("https://api.authsec.dev")

# Get token via OIDC or other method
token = client.exchange_oidc("oidc-code", "client-id")

# User is part of multiple projects
projects = ["project-A", "project-B", "project-C"]

# Check permissions for each project
for project_id in projects:
    can_read = client.check_permission_scoped(
        "document", "read", "project", project_id
    )
    can_write = client.check_permission_scoped(
        "document", "write", "project", project_id
    )
    can_delete = client.check_permission_scoped(
        "document", "delete", "project", project_id
    )
    
    permissions = []
    if can_read: permissions.append("read")
    if can_write: permissions.append("write")
    if can_delete: permissions.append("delete")
    
    print(f"Project {project_id}: {', '.join(permissions) or 'no access'}")

# Output:
# Project project-A: read, write, delete
# Project project-B: read, write
# Project project-C: read
```

---

## Need More Help?

- **Admin RBAC Management**: See [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)
- **API Documentation**: https://docs.authsec.dev
- **Interactive API Docs**: https://dev.api.authsec.dev/uflow/redoc
- **Support**: support@authsec.dev
- **GitHub Issues**: [Repository Issues](https://github.com/authsec-ai/authsec-python-sdk/issues)
