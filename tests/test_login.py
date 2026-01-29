#!/usr/bin/env python3
"""
Login Integration Test

Tests the new login() method against real user-flow API.

Prerequisites:
- User-flow service running (local or dev.api.authsec.dev)
- Valid test user with email/password in database
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

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

def test_login():
    """Test login() method"""
    print_info("\n=== Testing login() Method ===\n")
    
    # Get credentials from environment
    email = os.getenv("TEST_EMAIL", "test@example.com")
    password = os.getenv("TEST_PASSWORD", "test-password")
    client_id = os.getenv("TEST_CLIENT_ID", "test-client-uuid")
    base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev")
    
    print_info(f"Base URL: {base_url}")
    print_info(f"Email: {email}")
    print_info(f"Client ID: {client_id}")
    
    if email == "test@example.com":
        print_warning("\n⚠️  Using default test credentials!")
        print_warning("Set environment variables for real testing:")
        print_warning("  export TEST_EMAIL='user@example.com'")
        print_warning("  export TEST_PASSWORD='your-password'")
        print_warning("  export TEST_CLIENT_ID='your-client-uuid'")
        print_warning("  export UFLOW_BASE_URL='https://dev.api.authsec.dev'\n")
    
    try:
        client = AuthSecClient(base_url=base_url)
        
        print_info("Calling login()...")
        token = client.login(
            email=email,
            password=password,
            client_id=client_id
        )
        
        if token:
            print_success(f"Login successful!")
            print_info(f"  Token (first 50 chars): {token[:50]}...")
            
            # Decode token to show it's valid 
            import jwt
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                print_info(f"  Token claims: {list(decoded.keys())}")
                print_success("Token is valid JWT!")
            except Exception as e:
                print_warning(f"Could not decode token: {e}")
            
            return True
        else:
            print_error("Login returned None")
            return False
            
    except Exception as e:
        print_error(f"Login failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"  Status: {e.response.status_code}")
            print_error(f"  Response: {e.response.text}")
        return False

def test_deprecation_warning():
    """Test that generate_token() shows deprecation warning"""
    print_info("\n=== Testing Deprecation Warning ===\n")
    
    try:
        import warnings
        client = AuthSecClient(base_url="http://localhost:7469")
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                # This should trigger deprecation warning
                client.generate_token(
                    tenant_id="test",
                    project_id="test",
                    client_id="test",
                    email_id="test@test.com"
                )
            except:
                pass  # Ignore errors, we just want the warning
            
            if len(w) > 0 and issubclass(w[0].category, DeprecationWarning):
                print_success("Deprecation warning is working!")
                print_info(f"  Message: {w[0].message}")
                return True
            else:
                print_warning("No deprecation warning detected")
                return False
                
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Login Method Integration Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    success = True
    success = test_login() and success
    success = test_deprecation_warning() and success
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if success:
        print(f"{GREEN}✓ All login tests completed!{RESET}")
    else:
        print(f"{YELLOW}⚠ Some tests had issues - check output above{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
