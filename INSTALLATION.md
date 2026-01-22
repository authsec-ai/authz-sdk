# Installation Guide

Quick guide for installing and using the AuthSec SDK from this distribution package.

---

## Installation Methods

### Method 1: Install from Local Clone (Current Method)

Since the package files haven't been pushed to GitHub yet, install from a local clone:

```bash
# Clone the repository
git clone https://github.com/authsec-ai/authz-sdk.git
cd authz-sdk

# Install in development mode (changes reflected immediately)
pip install -e .

# Or regular install
pip install .
```

### Method 2: Install from GitHub (After Pushing Files)

Once the package files are committed and pushed to GitHub:

```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

**To enable this method, run:**
```bash
git add .
git commit -m "Add package files and SDK implementation"
git push origin main
```

### Method 3: Install from PyPI (Coming Soon)

Once published to PyPI:

```bash
pip install authsec-authz-sdk
```

> **Note:** See [PUBLISHING.md](PUBLISHING.md) for instructions on publishing to PyPI.

---

## Package Contents

This distribution package contains:

```
authz-sdk/
├── README.md                              # Main overview and navigation
├── AUTHENTICATION_AUTHORIZATION_GUIDE.md  # Complete guide for AuthSecClient
├── ADMIN_HELPER_GUIDE.md                  # Complete guide for AdminHelper
├── INSTALLATION.md                        # This file
├── authsec/                               # Python package
│   ├── __init__.py                        # Package initialization
│   ├── minimal.py                         # AuthSecClient implementation
│   └── admin_helper.py                    # AdminHelper implementation
├── pyproject.toml                         # Package metadata and dependencies
├── requirements.txt                       # Dependencies list
├── LICENSE                                # MIT License
├── CHANGELOG.md                           # Version history
├── MANIFEST.in                            # Package manifest
└── PUBLISHING.md                          # Publishing guide

```

---

## Quick Verification

After installation (using any method above), verify the SDK is working:

```python
# Test import
from authsec import AuthSecClient, AdminHelper
print("✓ AuthSec SDK imported successfully")

# Check version
import authsec
print(f"Version: {authsec.__version__}")
print(f"Package: authsec-authz-sdk")

# Initialize client (will fail without valid URL, but tests import)
try:
    client = AuthSecClient("https://api.authsec.dev")
    print("✓ AuthSecClient initialized")
except Exception as e:
    print(f"✓ SDK working (expected error without credentials)")
```

---

## Environment Setup

### 1. Create Environment File

```bash
cp .env.example .env
```

### 2. Configure Variables

Edit `.env` with your credentials:

```bash
# Authentication SDK
AUTH_BASE_URL=https://api.authsec.dev
CLIENT_ID=your-client-id

# Admin SDK
ADMIN_TOKEN=your-admin-token
ADMIN_BASE_URL=https://api.authsec.dev
ENDPOINT_TYPE=enduser  # or "admin"
```

### 3. Load in Your Application

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use in SDK
from authsec import AuthSecClient, AdminHelper

client = AuthSecClient(os.getenv("AUTH_BASE_URL"))
admin = AdminHelper.from_env()
```

---

## Dependencies

The SDK requires:

- **Python**: 3.7 or higher
- **requests**: 2.25.0 or higher (automatically installed)

### Optional Development Dependencies

```bash
pip install authsec[dev]
```

Includes:
- pytest (testing)
- pytest-cov (coverage)
- black (formatting)
- mypy (type checking)

---

## Building from Source

If you want to build the package yourself:

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# dist/authsec-1.0.0.tar.gz
# dist/authsec-1.0.0-py3-none-any.whl

# Install the wheel
pip install dist/authsec-1.0.0-py3-none-any.whl
```

---

## Troubleshooting

### Import Error: No module named 'authsec'

**Solution:**
```bash
pip install authsec
# or
pip install -e .  # if in the distribution folder
```

### Import Error: No module named 'requests'

**Solution:**
```bash
pip install requests>=2.25.0
```

### SSL Certificate Errors

**Solution:**
```python
# For development only - not recommended for production
import urllib3
urllib3.disable_warnings()

client = AuthSecClient("https://api.authsec.dev")
```

### Connection Timeout

**Solution:**
```python
# Increase timeout
client = AuthSecClient(
    "https://api.authsec.dev",
    timeout=30.0  # seconds
)

admin = AdminHelper(
    token="token",
    timeout=30  # seconds
)
```

---

## Next Steps

After installation:

1. **For Application Developers**: Read [AUTHENTICATION_AUTHORIZATION_GUIDE.md](AUTHENTICATION_AUTHORIZATION_GUIDE.md)
2. **For Administrators**: Read [ADMIN_HELPER_GUIDE.md](ADMIN_HELPER_GUIDE.md)
3. **For Overview**: Read [README.md](README.md)

---

## Support

- **Documentation**: https://docs.authsec.dev
- **Issues**: https://github.com/authsec-ai/authsec-python-sdk/issues
- **Email**: support@authsec.dev
