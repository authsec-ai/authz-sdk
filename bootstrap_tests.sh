#!/bin/bash
# Bootstrap E2E Testing with Token Input
# This script sets up the environment and runs token-based E2E tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
VENV_DIR="venv"
PYTHON_CMD="python3"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         AuthSec SDK - Bootstrap E2E Testing Suite             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
CLEAN=false
QUICK=false
ADMIN_ONLY=false
ENDUSER_ONLY=false

for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --admin-only)
            ADMIN_ONLY=true
            shift
            ;;
        --enduser-only)
            ENDUSER_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --clean          Clean rebuild (remove venv and reinstall)"
            echo "  --quick          Skip token input, use existing TEST_AUTH_TOKEN"
            echo "  --admin-only     Run only admin tests"
            echo "  --enduser-only   Run only end-user tests"
            echo "  --help           Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

# Step 1: Clean if requested
if [ "$CLEAN" = true ]; then
    echo -e "${YELLOW}🧹 Cleaning previous builds...${NC}"
    rm -rf "$VENV_DIR"
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    echo -e "${GREEN}✓ Clean complete${NC}"
    echo ""
fi

# Step 2: Create virtual environment if needed
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 3: Install SDK in development mode
echo -e "${BLUE}📚 Installing SDK in development mode...${NC}"
pip install -q -e .
echo -e "${GREEN}✓ SDK installed${NC}"
echo ""

# Step 4: Install test dependencies
echo -e "${BLUE}📦 Installing test dependencies...${NC}"
pip install -q pytest pytest-cov requests pyjwt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 5: Get authentication token
if [ "$QUICK" = false ]; then
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                  Authentication Required                       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}To run E2E tests, you need a JWT token.${NC}"
    echo ""
    echo -e "${BLUE}How to get your token:${NC}"
    echo "  1. Visit: ${GREEN}https://app.authsec.dev${NC}"
    echo "  2. Login with your credentials"
    echo "  3. Complete OTP/MFA verification"
    echo "  4. Copy your JWT token from:"
    echo "     - Dashboard settings, OR"
    echo "     - Browser DevTools → Application → Local Storage"
    echo ""
    
    # Check if token already exists in environment
    if [ -n "$TEST_AUTH_TOKEN" ]; then
        echo -e "${GREEN}✓ Found existing TEST_AUTH_TOKEN in environment${NC}"
        echo -e "${YELLOW}Press Enter to use it, or paste a new token:${NC}"
        echo -n "Token (leave empty to use existing): "
        read NEW_TOKEN
        
        if [ -n "$NEW_TOKEN" ]; then
            export TEST_AUTH_TOKEN="$NEW_TOKEN"
            echo -e "${GREEN}✓ Using new token${NC}"
        else
            echo -e "${GREEN}✓ Using existing token${NC}"
        fi
    else
        echo -e "${YELLOW}Paste your JWT token below and press Enter:${NC}"
        echo -n "Token: "
        read TEST_AUTH_TOKEN
        export TEST_AUTH_TOKEN
        
        if [ -z "$TEST_AUTH_TOKEN" ]; then
            echo -e "${RED}✗ Error: No token provided${NC}"
            echo -e "${YELLOW}Run the script again and provide a valid token${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✓ Token received (${#TEST_AUTH_TOKEN} characters)${NC}"
    fi
    
    echo ""
    
    # Optional: Get separate admin/enduser tokens
    echo -e "${BLUE}Optional: Provide separate tokens for admin/enduser tests${NC}"
    echo -e "${YELLOW}Press Enter to skip and use the same token for both${NC}"
    echo ""
    
    echo -n "Admin token (or press Enter to use same): "
    read TEST_ADMIN_TOKEN
    if [ -n "$TEST_ADMIN_TOKEN" ]; then
        export TEST_ADMIN_TOKEN
        echo -e "${GREEN}✓ Separate admin token provided${NC}"
    else
        export TEST_ADMIN_TOKEN="$TEST_AUTH_TOKEN"
        echo -e "${BLUE}ℹ Using same token for admin tests${NC}"
    fi
    
    echo -n "End-user token (or press Enter to use same): "
    read TEST_ENDUSER_TOKEN
    if [ -n "$TEST_ENDUSER_TOKEN" ]; then
        export TEST_ENDUSER_TOKEN
        echo -e "${GREEN}✓ Separate end-user token provided${NC}"
    else
        export TEST_ENDUSER_TOKEN="$TEST_AUTH_TOKEN"
        echo -e "${BLUE}ℹ Using same token for end-user tests${NC}"
    fi
    
    echo ""
else
    echo -e "${BLUE}ℹ Quick mode: Using existing environment token${NC}"
    
    if [ -z "$TEST_AUTH_TOKEN" ]; then
        echo -e "${RED}✗ Error: TEST_AUTH_TOKEN not set${NC}"
        echo -e "${YELLOW}Either:${NC}"
        echo "  1. Set TEST_AUTH_TOKEN environment variable, OR"
        echo "  2. Run without --quick flag to input token interactively"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Token found in environment${NC}"
    echo ""
fi

# Step 6: Run E2E tests
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Running E2E Tests                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Build test command
TEST_CMD="$PYTHON_CMD tests/test_e2e_token_based.py"

if [ "$ADMIN_ONLY" = true ]; then
    TEST_CMD="$TEST_CMD --admin-only"
    echo -e "${BLUE}ℹ Running admin tests only${NC}"
elif [ "$ENDUSER_ONLY" = true ]; then
    TEST_CMD="$TEST_CMD --enduser-only"
    echo -e "${BLUE}ℹ Running end-user tests only${NC}"
else
    echo -e "${BLUE}ℹ Running all tests (admin + end-user)${NC}"
fi

echo ""
echo -e "${BLUE}Executing: $TEST_CMD${NC}"
echo ""

# Run the tests
if $TEST_CMD; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✓✓✓ ALL TESTS PASSED! ✓✓✓                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Save token for next run (optional)
    echo -e "${BLUE}💡 Tip: To skip token input next time, export your token:${NC}"
    echo "   export TEST_AUTH_TOKEN='your-token-here'"
    echo "   $0 --quick"
    echo ""
    
    exit 0
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    ✗ TESTS FAILED ✗                           ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  • Check if your token is valid and not expired"
    echo "  • Visit https://app.authsec.dev to get a fresh token"
    echo "  • Ensure you have the required permissions"
    echo "  • Check the error messages above for details"
    echo ""
    exit 1
fi
