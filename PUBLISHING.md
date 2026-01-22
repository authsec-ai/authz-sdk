# Publishing to PyPI

This guide explains how to publish the authsec package to PyPI.

---

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org)
2. **API Token**: Generate an API token from your PyPI account settings
3. **Build Tools**: Already installed in the virtual environment

---

## Build Status

✅ **Distribution package built successfully!**

The following files have been created in the `dist/` directory:
- `authsec-1.0.0-py3-none-any.whl` - Wheel distribution (14KB)
- `authsec-1.0.0.tar.gz` - Source distribution (17KB)

---

## Publishing Steps

### 1. Test the Built Package Locally

```bash
# Install from the wheel file
pip install dist/authsec-1.0.0-py3-none-any.whl

# Or from the tarball
pip install dist/authsec-1.0.0.tar.gz

# Verify it works
python -c "from authsec import AuthSecClient, AdminHelper; print('✓ Package works!')"
```

### 2. Upload to TestPyPI (Recommended First)

TestPyPI allows you to test the publishing process without affecting the real package index:

```bash
# Activate the build environment
source build-env/bin/activate

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your-testpypi-api-token>
```

### 3. Test Install from TestPyPI

```bash
# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ --no-deps authsec

# Test it
python -c "from authsec import AuthSecClient; print('✓ TestPyPI package works!')"
```

### 4. Upload to PyPI (Production)

Once verified on TestPyPI, upload to the real PyPI:

```bash
# Activate the build environment
source build-env/bin/activate

# Upload to PyPI
twine upload dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your-pypi-api-token>
```

### 5. Verify on PyPI

After upload, the package will be available at:
- Package page: https://pypi.org/project/authsec/
- Install command: `pip install authsec`

---

## Configuration File Method (Recommended)

Instead of entering credentials each time, create a `~/.pypirc` file:

```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...your-token-here...

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZw...your-testpypi-token-here...
```

Then simply run:
```bash
twine upload --repository testpypi dist/*  # For TestPyPI
twine upload dist/*                          # For PyPI
```

---

## Rebuilding After Changes

If you make changes to the package, rebuild before publishing:

```bash
# Clean old builds
rm -rf dist/ build/ authsec.egg-info/

# Rebuild
source build-env/bin/activate
python -m build

# Upload new version
twine upload dist/*
```

---

## Version Management

To publish a new version:

1. Update version in `pyproject.toml`:
   ```toml
   [project]
   name = "authsec"
   version = "1.0.1"  # Increment version
   ```

2. Update `CHANGELOG.md` with changes

3. Update version in `authsec/__init__.py`:
   ```python
   __version__ = "1.0.1"
   ```

4. Rebuild and publish:
   ```bash
   rm -rf dist/ build/ authsec.egg-info/
   python -m build
   twine upload dist/*
   ```

---

## Troubleshooting

### Build Failed
- Check `pyproject.toml` syntax
- Ensure all files referenced in `MANIFEST.in` exist
- Verify Python version compatibility

### Upload Failed - "File already exists"
- You cannot re-upload the same version
- Increment the version number in `pyproject.toml`

### Upload Failed - "Invalid credentials"
- Verify your API token is correct
- Use `__token__` as username, not your PyPI username
- Check token has upload permissions

### Package Not Installing
- Verify dependencies in `requirements.txt` are correct
- Check Python version requirement (>=3.7)
- Test in a clean virtual environment

---

## Security Best Practices

1. **Never commit tokens** - Add `.pypirc` to `.gitignore`
2. **Use scoped tokens** - Create tokens for specific projects
3. **Rotate tokens regularly** - Update tokens periodically
4. **Use TestPyPI first** - Always test before production upload

---

## Next Steps After Publishing

1. Add PyPI badge to README.md (already included)
2. Announce the release
3. Monitor PyPI download statistics
4. Respond to user issues and feedback
5. Plan next version based on feedback
