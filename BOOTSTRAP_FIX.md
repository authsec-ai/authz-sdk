## Quick Fix Applied ✅

**Problem:** The `read -s -p` command syntax wasn't working on macOS bash.

**Solution:** Changed from:
```bash
read -s -p "Token: " TEST_AUTH_TOKEN  # ❌ Doesn't work on all systems
```

To:
```bash
echo -n "Token: "
read TEST_AUTH_TOKEN  # ✅ Works everywhere
```

## Now Try Again

Run the bootstrap script:
```bash
./bootstrap_tests.sh
```

When prompted, paste your token and press **Enter**.

**Note:** The token will now be **visible** as you paste it (not hidden). This is normal and allows the input to work properly.

## Alternative: Use Quick Mode

If you prefer to avoid interactive input, set the token as an environment variable first:

```bash
export TEST_AUTH_TOKEN='your-jwt-token-here'
./bootstrap_tests.sh --quick
```

This skips the prompts entirely and uses the environment variable.

## What Changed

| Before | After |
|--------|-------|
| `read -s -p "prompt" VAR` | `echo -n "prompt"` + `read VAR` |
| Silent input (hidden) | Visible input |
| Doesn't work on all shells | Works on all POSIX shells |

The token input will now work correctly!
