#!/usr/bin/env python3
"""
Comprehensive SDK Test - Register and Login Flow

Tests the complete flow:
1. Register a new user (returns OTP)
2. Login with the registered user
3. Validate token
"""

import sys
import os
import random
import string

# Add parent directory to path to import authsec
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

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def test_register_and_login():
    """Test complete register and login flow"""
    
    # Generate random test credentials
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_user = {
        "email": f"test{random_id}@sdktest.com",
        "name": f"Test User {random_id}",
        "password": "TestPassword123!",
        "tenant_domain": f"sdktest{random_id}"
    }
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}SDK Test - Register and Login Flow{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        # Initialize SDK client
        base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev/uflow")
        client = AuthSecClient(base_url=base_url)
        
        print_info(f"Base URL: {base_url}")
        print_info(f"Test User Email: {test_user['email']}")
        print_info(f"Tenant Domain: {test_user['tenant_domain']}")
        
        # Step 1: Register
        print(f"\n{BLUE}Step 1: Registration{RESET}")
        print_info("Calling client.register()...")
        
        register_response = client.register(
            email=test_user['email'],
            name=test_user['name'],
            password=test_user['password'],
            tenant_domain=test_user['tenant_domain']
        )
        
        print_success("Registration successful!")
        print_info(f"OTP: {register_response.get('otp', 'N/A')}")
        print_info(f"Message: {register_response.get('message', 'N/A')}")
        
        # Extract registration data
        client_id = register_response.get('client_id')
        returned_tenant_domain = register_response.get('tenant_domain', test_user['tenant_domain'])
        
        # Step 2: Login
        print(f"\n{BLUE}Step 2: Login{RESET}")
        
        # If we got a client_id from registration, use it
        if client_id:
            print_info(f"Using client_id from registration: {client_id}")
        else:
            print_warning("No client_id in registration response, continuing...")
            # For testing, we'll try to extract from message or use a placeholder
            # In the real flow, we'd need to verify OTP first to get client_id
            print_warning("Attempting login without client_id verification...")
            return False
        
        print_info("Calling client.login()...")
        
        token = client.login(
            email=test_user['email'],
            password=test_user['password'],
            client_id=client_id,
            tenant_domain=returned_tenant_domain
        )
        
        if token:
            print_success("Login successful!")
            print_info(f"Token (first 50 chars): {token[:50]}...")
            
            # Step 3: Validate token
            print(f"\n{BLUE}Step 3: Token Validation{RESET}")
            
            # Decode token to show it's valid
            import jwt
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                print_success("Token is valid JWT!")
                print_info(f"Token claims: {list(decoded.keys())}")
                print_info(f"Email: {decoded.get('email_id', 'N/A')}")
                print_info(f"Tenant ID: {decoded.get('tenant_id', 'N/A')}")
                print_info(f"Client ID: {decoded.get('client_id', 'N/A')}")
                
                print(f"\n{GREEN}{'='*70}{RESET}")
                print(f"{GREEN}✓✓✓ ALL TESTS PASSED!{RESET}")
                print(f"{GREEN}{'='*70}{RESET}\n")
                return True
                
            except Exception as e:
                print_warning(f"Could not decode token: {e}")
                return False
        else:
            print_error("Login returned None")
            return False
            
    except Exception as e:
        print_error(f"Test failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"  Status: {e.response.status_code}")
            print_error(f"  Response: {e.response.text}")
        
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_register_and_login()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
