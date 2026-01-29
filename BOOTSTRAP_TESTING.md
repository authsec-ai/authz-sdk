# Bootstrap Testing Guide

## Quick Start

Run the interactive bootstrap script to set up and run E2E tests:

```bash
./bootstrap_tests.sh
```

The script will:
1. ✅ Create/activate virtual environment
2. ✅ Install SDK in development mode  
3. ✅ Install test dependencies
4. ✅ **Prompt for your JWT token**
5. ✅ Run comprehensive E2E tests

## Getting Your Token

### Step 1: Login to AuthSec
Visit **https://app.authsec.dev** and:
1. Login with your credentials
2. Complete OTP/MFA verification
3. Navigate to your dashboard

### Step 2: Copy JWT Token
Get your token from one of these locations:
- **Dashboard Settings** → Copy token
- **Browser DevTools** → Application → Local Storage → Look for token
- **Network Tab** → Check Authorization headers

### Step 3: Paste Token
When the bootstrap script prompts:
```
Paste your JWT token below:
Token: [paste here]
```

## Usage Options

### Interactive Mode (Default)
Prompts for token input each time:
```bash
./bootstrap_tests.sh
```

### Quick Mode
Skip token input by using existing environment variable:
```bash
export TEST_AUTH_TOKEN='your-jwt-token-here'
./bootstrap_tests.sh --quick
```

### Clean Rebuild
Remove virtual environment and reinstall:
```bash
./bootstrap_tests.sh --clean
```

### Run Specific Tests
```bash
# Admin tests only
./bootstrap_tests.sh --admin-only

# End-user tests only
./bootstrap_tests.sh --enduser-only
```

### Combined Options
```bash
# Clean rebuild + admin tests only
./bootstrap_tests.sh --clean --admin-only

# Quick mode + end-user tests
export TEST_AUTH_TOKEN='token'
./bootstrap_tests.sh --quick --enduser-only
```

## Separate Tokens (Advanced)

For testing with different privilege levels, provide separate tokens:

```bash
./bootstrap_tests.sh
# Script will prompt:
# 1. Main token (required)
# 2. Admin token (optional, uses main if not provided)
# 3. End-user token (optional, uses main if not provided)
```

Or set them as environment variables:
```bash
export TEST_AUTH_TOKEN='general-token'
export TEST_ADMIN_TOKEN='admin-token'
export TEST_ENDUSER_TOKEN='enduser-token'
./bootstrap_tests.sh --quick
```

## What Gets Tested

The bootstrap script runs `tests/test_e2e_token_based.py`:

### Admin Tests (6 tests)
- ✅ Create permissions
- ✅ List permissions
- ✅ Create roles
- ✅ List roles
- ✅ Check permissions
- ✅ List user permissions

### End-User Tests (2 tests)
- ✅ List permissions
- ✅ Check permissions

### Total: 8 integration tests against live API

## Environment Variables

The script recognizes these variables:

| Variable | Purpose | Required |
|----------|---------|----------|
| `TEST_AUTH_TOKEN` | General authentication token | ✅ Yes |
| `TEST_ADMIN_TOKEN` | Admin-specific token | ❌ Optional |
| `TEST_ENDUSER_TOKEN` | End-user-specific token | ❌ Optional |

## Troubleshooting

### Token Not Working?
- **Check expiration**: Tokens typically expire after 24 hours
- **Get fresh token**: Visit https://app.authsec.dev and login again
- **Verify format**: Token should start with `eyJ`

### Tests Failing?
```bash
# Run with verbose output
python3 tests/test_e2e_token_based.py

# Check specific test
python3 tests/test_e2e_token_based.py --admin-only
```

### Environment Issues?
```bash
# Clean rebuild
./bootstrap_tests.sh --clean

# Check Python version (requires 3.7+)
python3 --version

# Manual venv activation
source venv/bin/activate
python3 -c "from authsec import AuthSecClient; print('✓ SDK import works')"
```

## Tips & Best Practices

### Save Token for Quick Testing
```bash
# Add to your ~/.bashrc or ~/.zshrc
export TEST_AUTH_TOKEN='your-long-lived-token'

# Then run tests quickly
./bootstrap_tests.sh --quick
```

### Use .env File (Development Only)
```bash
# Create .env file (gitignored)
cat > .env << EOF
TEST_AUTH_TOKEN=your-token-here
TEST_ADMIN_TOKEN=admin-token-here
EOF

# Load and run
source .env
./bootstrap_tests.sh --quick
```

⚠️ **Warning**: Never commit `.env` files to version control!

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run E2E Tests
  env:
    TEST_AUTH_TOKEN: ${{ secrets.AUTHSEC_TOKEN }}
  run: |
    chmod +x bootstrap_tests.sh
    ./bootstrap_tests.sh --quick
```

## Script Options Reference

```
Usage: ./bootstrap_tests.sh [OPTIONS]

Options:
  --clean          Clean rebuild (remove venv and reinstall)
  --quick          Skip token input, use existing TEST_AUTH_TOKEN
  --admin-only     Run only admin tests
  --enduser-only   Run only end-user tests
  --help           Show help message
```

## Expected Output

### Successful Run
```
╔════════════════════════════════════════════════════════════════╗
║         AuthSec SDK - Bootstrap E2E Testing Suite             ║
╚════════════════════════════════════════════════════════════════╝

✓ Virtual environment created
✓ SDK installed
✓ Dependencies installed
✓ Token received

╔════════════════════════════════════════════════════════════════╗
║                    Running E2E Tests                           ║
╚════════════════════════════════════════════════════════════════╝

Admin Operations:
  Passed (6):
    ✓ create_permission
    ✓ list_permissions
    ✓ create_role
    ✓ list_roles
    ✓ check_permission
    ✓ list_user_permissions

End-User Operations:
  Passed (2):
    ✓ list_permissions
    ✓ check_permission

Overall: Total Passed: 8, Total Failed: 0

╔════════════════════════════════════════════════════════════════╗
║              ✓✓✓ ALL TESTS PASSED! ✓✓✓                        ║
╚════════════════════════════════════════════════════════════════╝

💡 Tip: To skip token input next time, export your token:
   export TEST_AUTH_TOKEN='your-token-here'
   ./bootstrap_tests.sh --quick
```

## Security Notes

- ✅ Token is never written to disk by the script
- ✅ Token is passed via environment variables only
- ✅ Script uses `-s` flag for secure password input
- ⚠️ Be careful when exporting tokens in shell history
- 🔒 Use secrets managers in production environments

## Next Steps

After running tests successfully:
1. Review test results
2. Check coverage in test output
3. Run specific test suites as needed
4. Integrate into your CI/CD pipeline

For more information, see:
- [README_E2E_TESTS.md](../README_E2E_TESTS.md) - E2E testing guide
- [MIGRATION_LOGIN_REMOVAL.md](../MIGRATION_LOGIN_REMOVAL.md) - Token-based authentication
- [README.md](../README.md) - Main SDK documentation
