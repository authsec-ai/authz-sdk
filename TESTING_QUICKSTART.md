# Quick Start - Testing the SDK

This guide shows you how to test the AuthSec SDK with **zero manual setup** - everything is automated!

## 🚀 One-Command Testing

### Option 1: Full Automated Bootstrap (Recommended)

```bash
./bootstrap_tests.sh
```

This single command will:
1. ✅ Create a fresh virtual environment
2. ✅ Install the SDK in development mode
3. ✅ Install all test dependencies (pytest, coverage)
4. ✅ Run the complete test suite
5. ✅ Show test results and next steps

**No manual dependency installation needed!**

### Option 2: Quick Tests Only (No API Calls)

```bash
./bootstrap_tests.sh --quick
```

Runs only offline tests:
- SDK structure validation
- Endpoint configuration tests
- Method availability checks

Perfect for quick validation without API access.

### Option 3: Clean Rebuild

```bash
./bootstrap_tests.sh --clean
```

Removes all build artifacts and recreates everything from scratch.

---

## 📋 What Gets Tested

The automated test suite includes:

### ✅ Offline Tests (Always Pass)
- **SDK Structure** (`test_comprehensive.py`)
  - 5 test suites covering SDK imports, methods, and documentation
  
- **Endpoint Configuration** (`test_endpoint_switching.py`)
  - 7 tests validating admin/enduser endpoint switching

### 🌐 Online Tests (Require API Access)
- **Admin Flow** (`test_admin_flow.py`)
  - Admin registration (creates tenant)
  - Admin endpoint configuration
  
- **End-User Flow** (`test_enduser_flow.py`)
  - End-user registration (within tenant)
  - OTP verification flow
  
- **Dev Environment** (`test_dev_sdk.py`)
  - Live API testing against dev.api.authsec.dev

---

## 🎯 Test Results

After running `./bootstrap_tests.sh`, you'll see:

```
========================================
Test Summary
========================================

✓ Test bootstrap completed successfully!
ℹ Virtual environment: /path/to/authz-sdk/venv
ℹ To activate manually: source venv/bin/activate
ℹ To run tests again: python3 tests/test_comprehensive.py
```

### Expected Test Counts

| Test File | Tests | Expected Result |
|-----------|-------|-----------------|
| `test_comprehensive.py` | 5 suites | ✅ All pass |
| `test_endpoint_switching.py` | 7 tests | ✅ All pass |
| `test_admin_flow.py` | 4 tests | ✅ All pass* |
| `test_enduser_flow.py` | 4 tests | ✅ All pass* |
| `test_dev_sdk.py` | 4 tests | ✅ All pass* |

\* Requires API access to dev.api.authsec.dev

---

## 🔧 Manual Testing (If Needed)

If you want to run tests manually:

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Run Individual Tests

```bash
# Comprehensive SDK tests
python3 tests/test_comprehensive.py

# Endpoint switching tests
python3 tests/test_endpoint_switching.py

# Admin flow tests
python3 tests/test_admin_flow.py

# End-user flow tests
python3 tests/test_enduser_flow.py

# Dev environment tests
python3 tests/test_dev_sdk.py
```

### 3. Run with Pytest

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=authsec --cov-report=html

# View coverage
open htmlcov/index.html
```

---

## 🌍 Testing Against Different Environments

### Dev Environment (Default)

```bash
export UFLOW_BASE_URL="https://dev.api.authsec.dev/uflow"
python3 tests/test_admin_flow.py
```

### Custom Environment

```bash
export UFLOW_BASE_URL="https://your-api.example.com/uflow"
export TEST_CLIENT_ID="your-client-uuid"
python3 tests/test_enduser_flow.py
```

---

## 📦 Testing After Installation

### Test PyPI Installation

```bash
# Create clean environment
python3 -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install authsec-authz-sdk

# Test imports
python3 << 'EOF'
from authsec import AuthSecClient, AdminHelper

# Verify basic functionality
client = AuthSecClient("https://dev.api.authsec.dev")
print(f"✓ Endpoint type: {client.endpoint_type}")
print(f"✓ SDK version loaded successfully")
EOF

# Cleanup
deactivate
rm -rf test_env
```

---

## 🐛 Troubleshooting

### "Permission denied" Error

```bash
chmod +x bootstrap_tests.sh
./bootstrap_tests.sh
```

### Tests Fail with "Connection Error"

The API tests require internet access. Run quick tests only:

```bash
./bootstrap_tests.sh --quick
```

### "Module not found" Error

```bash
# Rebuild everything
./bootstrap_tests.sh --clean
```

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf venv
./bootstrap_tests.sh
```

---

## 📊 Continuous Integration

The bootstrap script works perfectly in CI/CD pipelines:

### GitHub Actions

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Run Bootstrap Tests
        run: ./bootstrap_tests.sh --quick
```

### GitLab CI

```yaml
test:
  script:
    - ./bootstrap_tests.sh --quick
```

---

## 🎓 What You Get

After running the bootstrap script:

1. **Virtual Environment**: `venv/` - Isolated Python environment
2. **Installed SDK**: Development mode (`pip install -e .`)
3. **Test Dependencies**: pytest, pytest-cov
4. **Test Results**: Full output showing all test results
5. **Next Steps**: Clear instructions on what to do next

---

## 💡 Pro Tips

### Run Tests Before Commits

```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
./bootstrap_tests.sh --quick
```

### Watch Mode During Development

```bash
source venv/bin/activate
pytest tests/ --watch
```

### Generate Coverage Badge

```bash
pytest tests/ --cov=authsec --cov-report=term-missing
```

---

## ✅ Quick Reference

```bash
# Full automated testing
./bootstrap_tests.sh

# Quick tests only
./bootstrap_tests.sh --quick

# Clean rebuild
./bootstrap_tests.sh --clean

# Help
./bootstrap_tests.sh --help

# Manual test activation
source venv/bin/activate
python3 tests/test_comprehensive.py
```

---

**That's it!** The bootstrap script handles everything automatically. Just run `./bootstrap_tests.sh` and you're ready to test! 🚀
