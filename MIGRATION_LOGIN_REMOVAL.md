# Migration Guide: Login Removal

## Why Login Was Removed

As of **2026-01-28**, the `login()` method has been removed from `AuthSecClient` because:

1. **OTP/MFA Required**: Authentication requires OTP/MFA verification which cannot be automated via SDK
2. **Security**: Multi-factor authentication must be completed through the secure web interface
3. **Best Practice**: Tokens should be obtained through the official web UI, not via programmatic login

## Migration Steps

### Before (Deprecated)

```python
from authsec import AuthSecClient

# ❌ This no longer works
client = AuthSecClient("https://dev.api.authsec.dev")
token = client.login(
    email="user@example.com",
    password="password",
    client_id="client-id",
    tenant_domain="tenant"
)
```

### After (Current)

#### Step 1: Get Your Token

Visit **https://app.authsec.dev** and:
1. Login with your credentials
2. Complete OTP/MFA verification
3. Copy your JWT token from the dashboard or browser DevTools

#### Step 2: Use Token-Based Initialization

```python
from authsec import AuthSecClient
import os

# ✅ Initialize with token
client = AuthSecClient(
    base_url="https://dev.api.authsec.dev",
    token=os.getenv('AUTHSEC_TOKEN'),  # Store token securely in environment
    endpoint_type="enduser"
)

# Use the SDK normally
if client.check_permission("document", "read"):
    print("Access granted")
```

#### Step 3: Store Token Securely

**Option A: Environment Variables (Recommended)**
```bash
export AUTHSEC_TOKEN='eyJhbGciOiJIUzI1NiIs...'
```

**Option B: .env File (Development Only)**
```bash
# .env (DO NOT COMMIT!)
AUTHSEC_TOKEN=eyJhbGciOiJIUzI1NiIs...
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('AUTHSEC_TOKEN')
```

**Option C: Secrets Manager (Production)**
```python
# AWS Secrets Manager, HashiCorp Vault, etc.
import boto3

client = boto3.client('secretsmanager')
token = client.get_secret_value(SecretId='authsec/token')['SecretString']
```

## Updated Code Examples

### Basic Permission Check

```python
from authsec import AuthSecClient
import os

# Initialize with token
client = AuthSecClient(
    base_url=os.getenv('AUTHSEC_API_URL', 'https://dev.api.authsec.dev'),
    token=os.getenv('AUTHSEC_TOKEN')
)

# Check permission
has_access = client.check_permission("document", "write")
if has_access:
    # Allow user to write document
    pass
```

### List User Permissions

```python
# Get all user permissions
permissions = client.list_permissions()

for perm in permissions:
    resource = perm.get('resource')
    actions = perm.get('actions', [])
    print(f"{resource}: {', '.join(actions)}")
```

### Admin Operations

```python
from authsec import AdminHelper
import os

# Admin operations require admin token
admin = AdminHelper(
    token=os.getenv('AUTHSEC_ADMIN_TOKEN'),
    base_url='https://dev.api.authsec.dev',
    endpoint_type='admin'
)

# Create permissions and roles
perm = admin.create_permission("document", "write", "Write documents")
role = admin.create_role("Editor", "Editor role", ["document:read", "document:write"])
```

## Breaking Changes

### Removed Methods

| Method | Status | Alternative |
|--------|--------|-------------|
| `client.login()` | ❌ Removed | Get token from https://app.authsec.dev |

### Updated Initialization

| Before | After |
|--------|-------|
| `AuthSecClient(base_url)` | `AuthSecClient(base_url, token=token)` |
| Login after init | Pass token during init |

## Frequently Asked Questions

### Q: How do I get a token?
**A:** Login at https://app.authsec.dev, complete MFA, then copy your JWT token from:
- Dashboard settings
- Browser DevTools → Application → Local Storage
- API response after web authentication

### Q: How long are tokens valid?
**A:** Check your token's `exp` claim. Typically 24 hours. Refresh tokens through the web interface.

### Q: Can I automate token refresh?
**A:** No. Tokens must be obtained through the web interface with MFA. This is a security feature.

### Q: What about CI/CD pipelines?
**A:** Use service account tokens or API keys. Contact support for service account setup.

### Q: How do I check token expiration?
```python
import jwt
import time

def is_token_expired(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get('exp', 0)
        return time.time() > exp
    except:
        return True

if is_token_expired(my_token):
    print("Token expired - get new token from web interface")
```

## Security Best Practices

### ✅ DO

- Store tokens in environment variables
- Use secrets managers in production
- Rotate tokens regularly
- Keep tokens out of source code
- Use `.gitignore` to exclude `.env` files

### ❌ DON'T

- Hardcode tokens in source code
- Commit tokens to git
- Share tokens between users
- Store tokens in plain text files
- Include tokens in logs

## Support

If you need help migrating:

1. Check the examples: `/examples/basic_auth.py`
2. Read the E2E testing guide: `README_E2E_TESTS.md`
3. View security audit: [security_audit.md](/.gemini/antigravity/brain/3fcb4404-febb-4064-9623-04a31ca4e69a/security_audit.md)
4. Contact: support@authsec.dev

## Timeline

- **2026-01-28**: `login()` method removed
- **Immediate**: Update all code to use token-based initialization
- **No deprecation period**: Change is immediate due to security requirements

## Summary

| Aspect | Old | New |
|--------|-----|-----|
| **Authentication** | SDK login | Web interface + token |
| **Initialization** | `AuthSecClient(url)` | `AuthSecClient(url, token=token)` |
| **Token Storage** | In-memory after login | Environment variable |
| **MFA** | Not supported | Required via web |
| **Security** | Medium | High |
