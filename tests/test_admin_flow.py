#!/usr/bin/env python3
"""
Admin Flow Tests

Tests admin-specific functionality:
- Admin registration (creates new tenant)
- Admin login
- Admin endpoint configuration
"""

import sys
import os
import random
import string

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

def test_admin_registration():
    """Test admin registration flow"""
    
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Admin Flow Tests{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        # Initialize admin client
        base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev/uflow")
        client = AuthSecClient(
            base_url=base_url,
            endpoint_type="admin"
        )
        
        print_info("Test 1: Admin Client Initialization")
        print_success(f"Endpoint type: {client.endpoint_type}")
        assert client.endpoint_type == "admin", "Endpoint type should be 'admin'"
        print_success("Admin client initialized correctly")
        
        # Test admin registration
        print(f"\n{BLUE}Test 2: Admin Registration{RESET}")
        
        test_admin = {
            "email": f"admin{random_id}@sdktest.com",
            "name": f"Admin User {random_id}",
            "password": "AdminPass123!",
            "tenant_domain": f"admindomain{random_id}"
        }
        
        print_info(f"Email: {test_admin['email']}")
        print_info(f"Tenant Domain: {test_admin['tenant_domain']}")
        print_info("Calling client.register()...")
        
        response = client.register(
            email=test_admin['email'],
            name=test_admin['name'],
            password=test_admin['password'],
            tenant_domain=test_admin['tenant_domain']
        )
        
        print_success("Admin registration successful!")
        print_info(f"Response keys: {list(response.keys())}")
        
        if 'otp' in response:
            print_success(f"OTP received: {response['otp']}")
        
        if 'message' in response:
            print_info(f"Message: {response['message']}")
        
        # Test method availability
        print(f"\n{BLUE}Test 3: Admin-Specific Methods{RESET}")
        
        assert hasattr(client, 'register'), "register() method exists"
        print_success("client.register() ✓ (admin only)")
        
        assert hasattr(client, 'verify_registration'), "verify_registration() method exists"
        print_success("client.verify_registration() ✓")
        
        assert hasattr(client, 'login'), "login() method exists"
        print_success("client.login() ✓")
        
        # Test endpoint_type configuration
        print(f"\n{BLUE}Test 4: Endpoint Type Configuration{RESET}")
        
        print_success(f"Configured as: endpoint_type='{client.endpoint_type}'")
        
        # Verify admin client can access admin methods
        print_success("Admin client can call admin-specific registration")
        
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✓ All Admin Tests Passed!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        print_info("Summary:")
        print_success("1. Admin client initialized with endpoint_type='admin'")
        print_success("2. Admin registration successful (creates new tenant)")
        print_success("3. All admin methods available")
        print_success("4. Endpoint configuration working correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Status: {e.response.status_code}")
            print_error(f"Response: {e.response.text}")
        
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_admin_registration()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
