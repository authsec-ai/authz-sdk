#!/usr/bin/env bash
#
# Automated PyPI Publishing Script
# 
# This script automates the entire PyPI publishing process:
# 1. Cleans previous builds
# 2. Builds distribution packages
# 3. Checks package validity
# 4. Uploads to PyPI (test or production)
#
# Usage:
#   ./publish_to_pypi.sh --test         # Publish to Test PyPI
#   ./publish_to_pypi.sh --production   # Publish to Production PyPI
#   ./publish_to_pypi.sh --help         # Show help
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Parse arguments
TARGET=""

for arg in "$@"; do
    case $arg in
        --test)
            TARGET="test"
            ;;
        --production)
            TARGET="production"
            ;;
        --help)
            echo "AuthSec SDK - PyPI Publishing Script"
            echo ""
            echo "Usage: $0 [option]"
            echo ""
            echo "Options:"
            echo "  --test         Publish to Test PyPI"
            echo "  --production   Publish to Production PyPI"
            echo "  --help         Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

if [ -z "$TARGET" ]; then
    print_error "Please specify --test or --production"
    echo "Run '$0 --help' for usage information"
    exit 1
fi

print_header "AuthSec SDK - PyPI Publishing"

# Check build tools
print_info "Checking build tools..."

if ! python3 -m pip show build &> /dev/null; then
    print_error "build module not found. Installing..."
    pip install build
fi

if ! python3 -m pip show twine &> /dev/null; then
    print_error "twine module not found. Installing..."
    pip install twine
fi

print_success "Build tools available"

# Step 1: Clean previous builds
print_header "Step 1: Cleaning Previous Builds"

rm -rf dist/ build/ *.egg-info
print_success "Cleaned dist/, build/, and *.egg-info"

# Step 2: Build distribution
print_header "Step 2: Building Distribution Packages"

python3 -m build

if [ -d "dist" ]; then
    print_success "Distribution packages built:"
    ls -lh dist/
else
    print_error "Build failed - dist/ directory not created"
    exit 1
fi

# Step 3: Check package
print_header "Step 3: Checking Package Validity"

python3 -m twine check dist/*
print_success "Package validation passed"

# Step 4: Upload
print_header "Step 4: Uploading to PyPI"

if [ "$TARGET" = "test" ]; then
    print_info "Uploading to Test PyPI..."
    print_info "URL: https://test.pypi.org/"
    echo ""
    python3 -m twine upload --repository testpypi dist/*
    
    print_success "Uploaded to Test PyPI!"
    echo ""
    print_info "Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ authsec-authz-sdk"
    echo ""
    print_info "View package at:"
    echo "  https://test.pypi.org/project/authsec-authz-sdk/"
    
elif [ "$TARGET" = "production" ]; then
    print_info "Uploading to Production PyPI..."
    print_info "URL: https://pypi.org/"
    echo ""
    
    # Ask for confirmation
    read -p "Are you sure you want to publish to PRODUCTION PyPI? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_error "Upload cancelled"
        exit 1
    fi
    
    python3 -m twine upload dist/*
    
    print_success "Uploaded to Production PyPI!"
    echo ""
    print_info "Installation command:"
    echo "  pip install authsec-authz-sdk"
    echo ""
    print_info "View package at:"
    echo "  https://pypi.org/project/authsec-authz-sdk/"
fi

print_header "Publishing Complete"
print_success "All done! 🚀"
