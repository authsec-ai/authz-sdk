# Installation & Setup Guide

Complete guide for installing and configuring the AuthSec SDK.

---

## Step 1: Install the SDK

```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

**Requirements:**
- Python 3.7 or higher
- `requests` library (auto-installed)

---

## Step 2: Get Your Credentials

Obtain these from your AuthSec dashboard at https://dashboard.authsec.dev:

1. **API URL** - Your AuthSec API endpoint (e.g., `https://api.authsec.dev`)
2. **Client ID** - Your application's client identifier
3. **Tenant ID** - Your organization's tenant identifier
4. **Admin Token** - Required only for RBAC management operations

---

## Step 3: Configure Environment Variables

### Option A: Export as Shell Variables

```bash
export AUTHSEC_API_URL="https://api.authsec.dev"
export AUTHSEC_CLIENT_ID="your-client-id"
export AUTHSEC_TENANT_ID="your-tenant-id"
export AUTHSEC_ADMIN_TOKEN="your-admin-token"  # Only for admin operations
```

### Option B: Create a `.env` File

```bash
# .env
AUTHSEC_API_URL=https://api.authsec.dev
AUTHSEC_CLIENT_ID=your-client-id
AUTHSEC_TENANT_ID=your-tenant-id
AUTHSEC_ADMIN_TOKEN=your-admin-token
```

Then load it in your code:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

### Option C: Set in Python Code

```python
import os

os.environ['AUTHSEC_API_URL'] = 'https://api.authsec.dev'
os.environ['AUTHSEC_CLIENT_ID'] = 'your-client-id'
os.environ['AUTHSEC_TENANT_ID'] = 'your-tenant-id'
os.environ['AUTHSEC_ADMIN_TOKEN'] = 'your-admin-token'
```

---

## Step 4: Verify Installation

```python
# Test import
from authsec import AuthSecClient, AdminHelper
print("✓ AuthSec SDK imported successfully")

# Check version
import authsec
print(f"Version: {authsec.__version__}")
```

---

## What to Do Next?

### For Application Developers (Authentication & Authorization)

Use **`AuthSecClient`** to:
- Authenticate users (login/logout)
- Check user permissions
- Verify access to resources

**📖 Read the complete guide:** [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)

**Quick example:**
```python
from authsec import AuthSecClient
import os

client = AuthSecClient(os.getenv('AUTHSEC_API_URL'))
token = client.login(
    email="user@example.com",
    password="password",
    client_id=os.getenv('AUTHSEC_CLIENT_ID')
)
```

### For Administrators (RBAC Management)

Use **`AdminHelper`** to:
- Create and manage roles
- Define permissions
- Assign roles to users
- Manage scopes

**📖 Read the complete guide:** [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)

**Quick example:**
```python
from authsec import AdminHelper
import os

admin = AdminHelper(
    token=os.getenv('AUTHSEC_ADMIN_TOKEN'),
    endpoint_type="admin"
)
role = admin.create_role(
    name="Editor",
    permission_strings=["document:read", "document:write"]
)
```

---

## Running Examples

The SDK includes working examples:

```bash
# Clone the repo to access examples
git clone https://github.com/authsec-ai/authz-sdk.git
cd authz-sdk/examples

# Set your environment variables first
export AUTHSEC_API_URL="https://api.authsec.dev"
export AUTHSEC_CLIENT_ID="your-client-id"

# Run an example
python basic_auth.py
```

---

## Troubleshooting

### Import Error: No module named 'authsec'

**Solution:**
```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

### Import Error: No module named 'requests'

**Solution:**
```bash
pip install requests>=2.25.0
```

### Connection Timeout

**Solution:**
```python
# Increase timeout
client = AuthSecClient(
    "https://api.authsec.dev",
    timeout=30.0  # seconds
)
```

---

## Support

- **Documentation**: https://docs.authsec.dev
- **Issues**: https://github.com/authsec-ai/authz-sdk/issues
- **Email**: support@authsec.dev
