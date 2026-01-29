# Publishing to PyPI - Quick Start Guide

This guide explains how to publish the AuthSec SDK to PyPI so users can install it with `pip install authsec-authz-sdk`.

## Prerequisites

1. **PyPI Account**: Create accounts on:
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

2. **API Tokens**: Generate API tokens:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - Production PyPI: https://pypi.org/manage/account/token/

3. **Install Build Tools**:
   ```bash
   pip install build twine
   ```

## Quick Publish (One Command)

```bash
# Clean, build, and publish to Test PyPI
./publish_to_pypi.sh --test

# Publish to Production PyPI  
./publish_to_pypi.sh --production
```

## Manual Steps

### Step 1: Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### Step 2: Build Distribution

```bash
python3 -m build
```

This creates:
- `dist/authsec_authz_sdk-1.0.0-py3-none-any.whl` (wheel)
- `dist/authsec-authz-sdk-1.0.0.tar.gz` (source)

### Step 3: Check Package

```bash
python3 -m twine check dist/*
```

Expected output:
```
Checking dist/authsec_authz_sdk-1.0.0-py3-none-any.whl: PASSED
Checking dist/authsec-authz-sdk-1.0.0.tar.gz: PASSED
```

### Step 4: Upload to Test PyPI (Recommended First)

```bash
python3 -m twine upload --repository testpypi dist/*
```

Enter your Test PyPI credentials when prompted.

### Step 5: Test Installation from Test PyPI

```bash
# Create test environment
python3 -m venv test_env
source test_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ authsec-authz-sdk

# Test it works
python3 -c "from authsec import AuthSecClient; print('Success!')"

# Clean up
deactivate
rm -rf test_env
```

### Step 6: Upload to Production PyPI

Once tested, upload to production:

```bash
python3 -m twine upload dist/*
```

Enter your Production PyPI credentials.

## Installation After Publishing

Users can then install with:

```bash
pip install authsec-authz-sdk
```

Or from GitHub (development):

```bash
pip install git+https://github.com/authsec-ai/authz-sdk.git
```

## Version Management

Update version in `pyproject.toml`:

```toml
[project]
name = "authsec-authz-sdk"
version = "1.0.1"  # Increment this
```

Version numbering:
- `1.0.0` → `1.0.1` - Bug fixes
- `1.0.0` → `1.1.0` - New features (backward compatible)
- `1.0.0` → `2.0.0` - Breaking changes

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

Add `PYPI_API_TOKEN` to GitHub repository secrets.

## Troubleshooting

### "File already exists" Error

PyPI doesn't allow re-uploading the same version. You must:
1. Increment version in `pyproject.toml`
2. Rebuild: `python3 -m build`
3. Upload again

### Authentication Failed

- Verify API token is correct
- Use `__token__` as username
- Token as password

### Import Errors After Install

Check package structure:
```bash
pip show authsec-authz-sdk
```

Verify:
```python
import authsec
print(authsec.__file__)  # Should show installed location
```

## Quick Reference

```bash
# Clean build
rm -rf dist/ build/ *.egg-info

# Build package
python3 -m build

# Check package
python3 -m twine check dist/*

# Upload to Test PyPI
python3 -m twine upload --repository testpypi dist/*

# Upload to Production PyPI
python3 -m twine upload dist/*
```

## Package Information

- **Package Name**: `authsec-authz-sdk`
- **Import Name**: `authsec`
- **PyPI URL**: https://pypi.org/project/authsec-authz-sdk/
- **Test PyPI URL**: https://test.pypi.org/project/authsec-authz-sdk/
