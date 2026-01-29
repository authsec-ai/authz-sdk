#!/bin/bash
# Test runner for AuthSec SDK

set -e

echo "====================================="
echo "AuthSec SDK Test Suite"
echo "====================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test type from argument
TEST_TYPE="${1:-all}"

run_comprehensive() {
    echo -e "${GREEN}Running comprehensive tests...${NC}"
    python3 tests/test_comprehensive.py
}

run_integration() {
    echo -e "${YELLOW}Running integration tests (requires database)...${NC}"
    if python3 tests/test_integration.py; then
        echo -e "${GREEN}✓ Integration tests passed${NC}"
    else
        echo -e "${RED}✗ Integration tests failed${NC}"
        return 1
    fi
}

run_login() {
    echo -e "${YELLOW}Running login tests (requires credentials)...${NC}"
    if python3 tests/test_login.py; then
        echo -e "${GREEN}✓ Login tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Login tests failed (check credentials)${NC}"
        return 1
    fi
}

run_pytest() {
    echo -e "${GREEN}Running pytest...${NC}"
    if command -v pytest &> /dev/null; then
        pytest tests/ -v
    else
        echo -e "${YELLOW}pytest not installed. Install with: pip install pytest${NC}"
        return 1
    fi
}

case "$TEST_TYPE" in
    "comprehensive" | "comp")
        run_comprehensive
        ;;
    "integration" | "int")
        run_integration
        ;;
    "login")
        run_login
        ;;
    "pytest")
        run_pytest
        ;;
    "all")
        echo "Running all available tests..."
        echo ""
        run_comprehensive
        echo ""
        echo "=====================================" 
        echo "Skipping integration tests (require database)"
        echo "Run './tests/run_tests.sh integration' to run them"
        echo "====================================="
        ;;
    *)
        echo "Usage: $0 [comprehensive|integration|login|pytest|all]"
        echo ""
        echo "Options:"
        echo "  comprehensive  - Run comprehensive structure tests (no deps)"
        echo "  integration    - Run database integration tests (requires PostgreSQL)"
        echo "  login          - Run login authentication tests (requires credentials)"
        echo "  pytest         - Run all tests with pytest"
        echo "  all            - Run all available tests (default)"
        exit 1
        ;;
esac

echo ""
echo "====================================="
echo "Test run complete!"
echo "====================================="
