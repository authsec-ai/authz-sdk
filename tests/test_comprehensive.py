#!/usr/bin/env python3
"""
Comprehensive SDK Integration Test
Tests all SDK functionality to ensure examples and documentation are accurate
"""

import sys
import os

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def test_imports():
    """Test 1: SDK imports"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST 1: SDK Imports{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        from authsec import AuthSecClient, AdminHelper
        print_success("Imported AuthSecClient and AdminHelper")
        return True
    except Exception as e:
        print_error(f"Import failed: {e}")
        return False

def test_authsecclient():
    """Test 2: AuthSecClient functionality"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST 2: AuthSecClient{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    from authsec import AuthSecClient
    
    errors = []
    
    # Test initialization
    try:
        client = AuthSecClient("https://dev.api.authsec.dev")
        print_success("Client initialized")
    except Exception as e:
        errors.append(f"Initialization failed: {e}")
        return len(errors) == 0
    
    # Test with token parameter
    try:
        client_with_token = AuthSecClient("https://dev.api.authsec.dev", token="test-token")
        print_success("Client initialized with token parameter")
    except Exception as e:
        errors.append(f"Token parameter initialization failed: {e}")
    
    # Test method existence
    required_methods = [
        'login',
        'exchange_oidc',
        'set_token',
        'check_permission',
        'check_permission_scoped',
        'list_permissions',
        'assign_role',
        'list_role_bindings',
        'remove_role_binding',
        'request'
    ]
    
    for method in required_methods:
        if hasattr(client, method) and callable(getattr(client, method)):
            print_success(f"Method exists: {method}")
        else:
            errors.append(f"Missing method: {method}")
            print_error(f"Missing method: {method}")
    
    # Test token setting
    try:
        client.set_token("test-jwt-token")
        if client.token == "test-jwt-token":
            print_success("Token setting works")
        else:
            errors.append("Token not set correctly")
    except Exception as e:
        errors.append(f"Token setting failed: {e}")
    
    # Test configuration options
    try:
        client_custom = AuthSecClient(
            base_url="https://api.authsec.dev",
            timeout=10.0,
            legacy_proxy_mode=False,
            uflow_base_url="https://uflow.authsec.dev"
        )
        print_success("Custom configuration works")
    except Exception as e:
        errors.append(f"Custom configuration failed: {e}")
    
    if errors:
        print(f"\n{RED}Errors:{RESET}")
        for error in errors:
            print(f"  {RED}•{RESET} {error}")
    
    return len(errors) == 0

def test_adminhelper():
    """Test 3: AdminHelper functionality"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST 3: AdminHelper{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    from authsec import AdminHelper
    
    errors = []
    
    # Test initialization
    try:
        admin = AdminHelper(token="test-token")
        print_success("AdminHelper initialized")
    except Exception as e:
        errors.append(f"Initialization failed: {e}")
        return len(errors) == 0
    
    # Test endpoint types
    try:
        admin_enduser = AdminHelper(token="test", endpoint_type="enduser")
        print_success("Enduser endpoint type works")
        
        admin_admin = AdminHelper(token="test", endpoint_type="admin")
        print_success("Admin endpoint type works")
    except Exception as e:
        errors.append(f"Endpoint type configuration failed: {e}")
    
    # Test method existence
    required_methods = [
        'create_permission',
        'list_permissions',
        'create_role',
        'list_roles',
        'get_role',
        'update_role',
        'delete_role',
        'create_role_binding',
        'list_role_bindings',
        'remove_role_binding',
        'create_scope',
        'list_scopes',
        'create_secret',
        'list_secrets',
        'from_env'
    ]
    
    for method in required_methods:
        if hasattr(admin, method) and callable(getattr(admin, method)):
            print_success(f"Method exists: {method}")
        else:
            errors.append(f"Missing method: {method}")
            print_error(f"Missing method: {method}")
    
    # Test from_env class method
    try:
        os.environ['ADMIN_TOKEN'] = 'test-env-token'
        os.environ['ADMIN_BASE_URL'] = 'https://test.com'
        os.environ['ENDPOINT_TYPE'] = 'admin'
        
        admin_env = AdminHelper.from_env()
        print_success("from_env() class method works")
        
        # Cleanup
        del os.environ['ADMIN_TOKEN']
        del os.environ['ADMIN_BASE_URL']
        del os.environ['ENDPOINT_TYPE']
    except Exception as e:
        errors.append(f"from_env() failed: {e}")
    
    if errors:
        print(f"\n{RED}Errors:{RESET}")
        for error in errors:
            print(f"  {RED}•{RESET} {error}")
    
    return len(errors) == 0

def test_distribution_package():
    """Test 4: Distribution package structure"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST 4: Package Structure{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    errors = []
    
    # Check root directory files (this repo is the package itself)
    required_files = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "requirements.txt",
        "authsec/__init__.py",
        "authsec/minimal.py",
        "authsec/admin_helper.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print_success(f"File exists: {file}")
        else:
            errors.append(f"Missing file: {file}")
            print_error(f"Missing file: {file}")
    
    # Test that SDK can be imported
    try:
        from authsec import AuthSecClient as PackageClient, AdminHelper as PackageAdmin
        print_success("Package SDK imports successfully")
    except Exception as e:
        errors.append(f"Package SDK import failed: {e}")
    
    return len(errors) == 0


def test_documentation_accuracy():
    """Test 5: Documentation accuracy"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST 5: Documentation Accuracy{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    from authsec import AuthSecClient, AdminHelper
    
    errors = []
    warnings = []
    
    # Check that documented methods in auth.md exist
    auth_methods_documented = [
        ('AuthSecClient', 'exchange_oidc'),
        ('AuthSecClient', 'set_token'),
        ('AuthSecClient', 'check_permission'),
        ('AuthSecClient', 'check_permission_scoped'),
        ('AuthSecClient', 'list_permissions'),
        ('AuthSecClient', 'assign_role'),
        ('AuthSecClient', 'list_role_bindings'),
        ('AuthSecClient', 'remove_role_binding'),
        ('AuthSecClient', 'request'),
    ]
    
    client = AuthSecClient("https://dev.api.authsec.dev")
    
    for class_name, method_name in auth_methods_documented:
        if hasattr(client, method_name):
            print_success(f"{class_name}.{method_name} exists (as documented)")
        else:
            errors.append(f"Documented method missing: {class_name}.{method_name}")
            print_error(f"Documented method missing: {class_name}.{method_name}")
    
    # Check AdminHelper methods
    admin_methods_documented = [
        ('AdminHelper', 'create_role'),
        ('AdminHelper', 'list_roles'),
        ('AdminHelper', 'get_role'),
        ('AdminHelper', 'update_role'),
        ('AdminHelper', 'delete_role'),
        ('AdminHelper', 'create_permission'),
        ('AdminHelper', 'list_permissions'),
        ('AdminHelper', 'create_role_binding'),
        ('AdminHelper', 'list_role_bindings'),
        ('AdminHelper', 'remove_role_binding'),
        ('AdminHelper', 'create_scope'),
        ('AdminHelper', 'list_scopes'),
        ('AdminHelper', 'create_secret'),
        ('AdminHelper', 'list_secrets'),
    ]
    
    admin = AdminHelper(token="test")
    
    for class_name, method_name in admin_methods_documented:
        if hasattr(admin, method_name):
            print_success(f"{class_name}.{method_name} exists (as documented)")
        else:
            errors.append(f"Documented method missing: {class_name}.{method_name}")
            print_error(f"Documented method missing: {class_name}.{method_name}")
    
    # Check for login method (should still exist in code even though removed from docs)
    if hasattr(client, 'login'):
        print_warning("AuthSecClient.login still exists in code (not documented)")
        warnings.append("login method exists but not documented")
    
    if errors:
        print(f"\n{RED}Errors:{RESET}")
        for error in errors:
            print(f"  {RED}•{RESET} {error}")
    
    if warnings:
        print(f"\n{YELLOW}Warnings:{RESET}")
        for warning in warnings:
            print(f"  {YELLOW}•{RESET} {warning}")
    
    return len(errors) == 0

def run_all_tests():
    """Run all tests"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}AuthSec SDK - Comprehensive Integration Test{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    results = {
        "Imports": test_imports(),
        "AuthSecClient": test_authsecclient(),
        "AdminHelper": test_adminhelper(),
        "Package Structure": test_distribution_package(),
        "Documentation Accuracy": test_documentation_accuracy()
    }

    
    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BLUE}Result: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✓ ALL TESTS PASSED{RESET}\n")
        return 0
    else:
        print(f"\n{RED}✗ SOME TESTS FAILED{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
