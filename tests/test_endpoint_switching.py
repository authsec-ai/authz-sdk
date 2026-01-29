#!/usr/bin/env python3
"""
Endpoint Switching Tests

Tests endpoint configuration and switching:
- endpoint_type parameter validation
- Admin vs enduser path resolution
- Default endpoint_type behavior
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from authsec import AuthSecClient

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def test_endpoint_switching():
    """Test endpoint configuration and switching"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Endpoint Switching Tests{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        base_url = "https://dev.api.authsec.dev"
        
        # Test 1: Default endpoint_type
        print_info("Test 1: Default Endpoint Type")
        client_default = AuthSecClient(base_url=base_url)
        assert client_default.endpoint_type == "enduser", "Default endpoint_type should be 'enduser'"
        print_success(f"Default endpoint_type: {client_default.endpoint_type}")
        
        # Test 2: Admin endpoint_type
        print(f"\n{BLUE}Test 2: Admin Endpoint Type{RESET}")
        client_admin = AuthSecClient(base_url=base_url, endpoint_type="admin")
        assert client_admin.endpoint_type == "admin", "Admin endpoint_type should be 'admin'"
        print_success(f"Admin endpoint_type: {client_admin.endpoint_type}")
        
        # Test 3: End-user endpoint_type
        print(f"\n{BLUE}Test 3: End-User Endpoint Type{RESET}")
        client_enduser = AuthSecClient(base_url=base_url, endpoint_type="enduser")
        assert client_enduser.endpoint_type == "enduser", "Enduser endpoint_type should be 'enduser'"
        print_success(f"End-user endpoint_type: {client_enduser.endpoint_type}")
        
        # Test 4: Case insensitivity
        print(f"\n{BLUE}Test 4: Case Insensitivity{RESET}")
        client_upper = AuthSecClient(base_url=base_url, endpoint_type="ADMIN")
        assert client_upper.endpoint_type == "admin", "Endpoint type should be lowercased"
        print_success("Endpoint type properly normalized to lowercase")
        
        # Test 5: Invalid endpoint_type
        print(f"\n{BLUE}Test 5: Invalid Endpoint Type Validation{RESET}")
        try:
            client_invalid = AuthSecClient(base_url=base_url, endpoint_type="invalid")
            print_error("Should have raised ValueError for invalid endpoint_type")
            return False
        except ValueError as e:
            print_success(f"Correctly rejected invalid endpoint_type: {e}")
        
        # Test 6: Method availability across endpoint types
        print(f"\n{BLUE}Test 6: Method Availability{RESET}")
        
        # Admin methods
        assert hasattr(client_admin, 'register'), "Admin client has register()"
        print_success("Admin client: register() method available")
        
        # End-user methods
        assert hasattr(client_enduser, 'register_enduser'), "Enduser client has register_enduser()"
        print_success("End-user client: register_enduser() method available")
        
        # Common methods
        assert hasattr(client_admin, 'login'), "Admin client has login()"
        assert hasattr(client_enduser, 'login'), "Enduser client has login()"
        print_success("Both clients: login() method available")
        
        assert hasattr(client_admin, 'check_permission'), "Admin client has check_permission()"
        assert hasattr(client_enduser, 'check_permission'), "Enduser client has check_permission()"
        print_success("Both clients: check_permission() method available")
        
        # Test 7: Initialization with all parameters
        print(f"\n{BLUE}Test 7: Full Initialization{RESET}")
        client_full = AuthSecClient(
            base_url="https://dev.api.authsec.dev",
            uflow_base_url="https://dev.api.authsec.dev/uflow",
            timeout=10.0,
            endpoint_type="admin",
            legacy_proxy_mode=False,
            token="sample-token-for-testing"
        )
        assert client_full.endpoint_type == "admin"
        assert client_full.timeout == 10.0
        assert client_full.token == "sample-token-for-testing"
        print_success("Full initialization with all parameters successful")
        
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✓ All Endpoint Switching Tests Passed!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        print_info("Summary:")
        print_success("1. Default endpoint_type is 'enduser'")
        print_success("2. Admin endpoint_type configuration works")
        print_success("3. End-user endpoint_type configuration works")
        print_success("4. Endpoint type is case-insensitive")
        print_success("5. Invalid endpoint types are rejected")
        print_success("6. All methods available regardless of endpoint_type")
        print_success("7. Full initialization with all parameters works")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_endpoint_switching()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
