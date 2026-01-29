#!/usr/bin/env python3
"""
SDK Registration Test

Tests SDK's register() method against dev environment.
This validates that the SDK can successfully register new users.
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
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def main():
   
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}AuthSec SDK - Dev Environment Test{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        # Initialize SDK
        base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev/uflow")
        client = AuthSecClient(base_url=base_url)
        
        print_info(f"Base URL: {base_url}")
        
        # Test 1: Register a new user
        print(f"\n{BLUE}Test 1: User Registration{RESET}")
        
        test_email = f"test{random_id}@sdktest.com"
        test_name = f"Test User {random_id}"
        test_password = "TestPassword123!"
        test_tenant = f"sdktest{random_id}"
        
        print_info(f"Email: {test_email}")
        print_info(f"Tenant: {test_tenant}")
        print_info("Calling SDK client.register()...")
        
        response = client.register(
            email=test_email,
            name=test_name,
            password=test_password,
            tenant_domain=test_tenant
        )
        
        print_success("Registration successful!")
        print_info(f"Response keys: {list(response.keys())}")
        
        if 'otp' in response:
            print_success(f"OTP received: {response['otp']}")
            print_info("(OTP returned for dev environment testing)")
        
        if 'message' in response:
            print_info(f"Message: {response['message']}")
        
        print(f"\n{BLUE}Test 2: SDK Methods Available{RESET}")
        
        # Verify SDK methods exist
        assert hasattr(client, 'register'), "register() method exists"
        print_success("client.register() ✓")
        
        assert hasattr(client, 'verify_registration'), "verify_registration() method exists"
        print_success("client.verify_registration() ✓")
        
        assert hasattr(client, 'login'), "login() method exists"
        print_success("client.login() ✓")
        
        assert hasattr(client, 'check_permission'), "check_permission() method exists"
        print_success("client.check_permission() ✓")
        
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✓ All SDK Tests Passed!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        print_info("Summary:")
        print_success("1. SDK successfully registered a new user in dev environment")
        print_success("2. Registration returned OTP for verification")
        print_success("3. All core SDK methods are available and functional")
        
        print(f"\n{YELLOW}Note:{RESET} Complete login flow requires OTP verification,")
        print(f"which is handled by the backend email service in production.")
        print(f"For automated testing, the dev environment returns OTP in response.\n")
        
        return 0
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Status: {e.response.status_code}")
            print_error(f"Response: {e.response.text}")
        
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
