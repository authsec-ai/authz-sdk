# AuthSec SDK Examples

This directory contains working examples demonstrating how to use the AuthSec SDK for various use cases.

## 📚 Available Examples

### 1. Basic Authentication (`basic_auth.py`)

**What it demonstrates:**
- Initializing the AuthSecClient
- Logging in with email and password
- Checking simple permissions
- Checking scoped permissions
- Listing user permissions
- Using pre-authenticated tokens
- OIDC token exchange

**Run it:**
```bash
python3 basic_auth.py
```

**Key code snippets:**
```python
# Login
client = AuthSecClient("https://dev.api.authsec.dev")
token = client.login(email="user@example.com", password="pass", client_id="...")

# Check permission
can_read = client.check_permission("document", "read")

# Scoped permission
can_write = client.check_permission_scoped("document", "write", "project", project_id)
```

---

### 2. Role Management (`role_management.py`)

**What it demonstrates:**
- Assigning roles to users
- Creating scoped role bindings
- Listing role bindings
- Removing role bindings
- Working with conditions
- Admin vs user endpoints

**Run it:**
```bash
python3 role_management.py
```

**Key code snippets:**
```python
# Assign role (tenant-wide)
binding = client.assign_role(user_id, role_id)

# Assign scoped role
scoped_binding = client.assign_role(
    user_id, role_id,
    scope_type="project",
    scope_id=project_id
)

# List bindings
bindings = client.list_role_bindings(user_id=user_id)
```

---

### 3. Admin RBAC Management (`admin_rbac.py`)

**What it demonstrates:**
- Creating permissions
- Creating and managing roles
- Updating roles
- Creating role bindings with scopes
- Managing API scopes
- Admin vs enduser endpoints
- Batch operations

**Run it:**
```bash
python3 admin_rbac.py
```

**Key code snippets:**
```python
from authsec import AdminHelper

# Initialize
admin = AdminHelper(token="admin-token", endpoint_type="enduser")

# Create permission
perm = admin.create_permission("document", "write", "Write documents")

# Create role
role = admin.create_role(
    "Editor",
    permission_strings=["document:read", "document:write"]
)

# Create binding
binding = admin.create_role_binding(user_id, role['id'])
```

---

### 4. Environment Configuration (`environment_config.py`)

**What it demonstrates:**
- Using environment variables
- AdminHelper.from_env() usage
- Using .env files with python-dotenv
- Production secret management
- Multi-environment configuration

**Run it:**
```bash
python3 environment_config.py
```

**Key code snippets:**
```python
# From environment
admin = AdminHelper.from_env()

# Using .env file
from dotenv import load_dotenv
load_dotenv()

# Multi-environment config
env = os.getenv("APP_ENV", "development")
config = environments[env]
```

---

## 🔧 Setup Instructions

### 1. Install the SDK

**From GitHub:**
```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

**Or from local clone (for development):**
```bash
cd ..
pip install -e .
```

### 2. Set Up Credentials

Create a `.env` file or set environment variables:

```bash
export AUTH_BASE_URL="https://dev.api.authsec.dev"
export CLIENT_ID="your-client-id"
export ADMIN_TOKEN="your-admin-token"
```

### 3. Update Example Code

Edit the example files to use your actual:
- Email and password
- Client ID
- User IDs
- Role IDs
- Project IDs

### 4. Run Examples

```bash
python3 basic_auth.py
python3 role_management.py
python3 admin_rbac.py
python3 environment_config.py
```

---

## 📖 Learning Path

**New to AuthSec?** Follow this learning path:

1. **Start with `basic_auth.py`**
   - Learn authentication basics
   - Understand permission checking
   - Get familiar with the client API

2. **Try `role_management.py`**
   - Learn role assignment
   - Understand scoped permissions
   - See role binding management

3. **Explore `admin_rbac.py`**
   - Learn complete RBAC workflow
   - Understand admin operations
   - See permission and role creation

4. **Configure with `environment_config.py`**
   - Learn production-ready configuration
   - Understand environment management
   - See secret management patterns

---

## 🎯 Common Use Cases

### Use Case 1: Simple User Login

```python
from authsec import AuthSecClient

client = AuthSecClient("https://dev.api.authsec.dev")
token = client.login(
    email="user@example.com",
    password="password",
    client_id="client-id"
)
```

### Use Case 2: Check If User Can Perform Action

```python
can_edit = client.check_permission("document", "write")
if can_edit:
    # Allow editing
else:
    # Show read-only view
```

### Use Case 3: Assign Role to New User

```python
from authsec import AdminHelper

admin = AdminHelper(token="admin-token")
viewer_role_id = "role-uuid-123"

binding = admin.create_role_binding(new_user_id, viewer_role_id)
```

### Use Case 4: Create Project-Specific Role

```python
# Create role
editor_role = admin.create_role(
    "Project Editor",
    permission_strings=["project:read", "project:write"]
)

# Assign to user for specific project
binding = admin.create_role_binding(
    user_id,
    editor_role['id'],
    scope_type="project",
    scope_id=project_id
)
```

---

## 💡 Tips & Best Practices

1. **Always handle exceptions**
   ```python
   try:
       token = client.login(...)
   except requests.HTTPError as e:
       print(f"Login failed: {e}")
   ```

2. **Use environment variables for secrets**
   ```python
   # Don't hardcode tokens!
   token = os.getenv("ADMIN_TOKEN")
   admin = AdminHelper(token=token)
   ```

3. **Check permissions before operations**
   ```python
   if client.check_permission("document", "delete"):
       delete_document()
   else:
       show_error("Permission denied")
   ```

4. **Use scoped permissions for multi-tenant apps**
   ```python
   can_access = client.check_permission_scoped(
       "data", "read",
       "tenant", tenant_id
   )
   ```

---

## 🔗 Additional Resources

- **Main Documentation**: [../README.md](../README.md)
- **Installation Guide**: [../INSTALLATION.md](../INSTALLATION.md)
- **Authentication Guide**: [../AUTHENTICATION_AUTHORIZATION_GUIDE.md](../AUTHENTICATION_AUTHORIZATION_GUIDE.md)
- **Admin Guide**: [../ADMIN_HELPER_GUIDE.md](../ADMIN_HELPER_GUIDE.md)
- **API Reference**: https://docs.authsec.dev

---

## 🤝 Contributing Examples

Have a useful example? Contributions are welcome!

1. Create a new Python file in this directory
2. Add comprehensive comments
3. Include error handling
4. Update this README
5. Submit a pull request

---

**Need Help?** Check the main [README](../README.md) or reach out to support@authsec.dev
