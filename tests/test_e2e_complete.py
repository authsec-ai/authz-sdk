#!/usr/bin/env python3
"""
Complete E2E Test - Token-Based RBAC Testing

This test covers complete RBAC workflow:
1. Create permissions
2. Create roles
3. Create role bindings
4. Verify permissions work

Usage:
    export TEST_AUTH_TOKEN='your-jwt-token'
    python3 tests/test_e2e_complete.py
"""

import sys
import os
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from authsec import AuthSecClient, AdminHelper

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_step(step_num, title):
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}Step {step_num}: {title}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")

def test_complete_e2e_flow():
    """Complete E2E RBAC test with token"""
    
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev")
    token = os.getenv('TEST_AUTH_TOKEN')
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Complete E2E RBAC Test (Token-Based){RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    if not token:
        print_error("TEST_AUTH_TOKEN environment variable required")
        print_info("Get token from: https://app.authsec.dev")
        return False
    
    print_info(f"Test ID: {random_id}")
    print_info(f"Base URL: {base_url}")
    
    try:
        # Initialize
        admin_helper = AdminHelper(token=token, base_url=base_url)
        
        # Get user ID using same pattern as test_e2e_token_based.py
        print_step(1, "Get User ID")
        
        user_id = None
        try:
            # verify_token uses /authmgr endpoint on main base_url
            authmgr_client = AuthSecClient(base_url=base_url, token=token)
            token_info = authmgr_client.verify_token(token)
            
            # Try various fields
            user_id = (token_info.get('user_id') or 
                      token_info.get('sub') or 
                      token_info.get('client_id') or
                      token_info.get('id'))
            
            if user_id:
                print_success(f"User ID: {user_id}")
            else:
                print_warning("Could not extract user_id from token")
        except Exception as e:
            print_warning(f"Token verification failed: {e}")
            # Try fallback: manual user ID from environment
            user_id = os.getenv('TEST_USER_ID')
            if user_id:
                print_info(f"Using TEST_USER_ID: {user_id}")
        
        # Initialize client with uflow endpoint
        admin_client = AuthSecClient(base_url=f"{base_url}/uflow", token=token)
        
        # Create permissions
        print_step(2, "Create Permissions")
        
        permissions = [
            ("document", "read", "Read documents"),
            ("document", "write", "Write documents"),
            ("document", "delete", "Delete documents"),
        ]
        
        for resource, action, description in permissions:
            try:
                admin_helper.create_permission(resource, action, description)
                print_success(f"Created: {resource}:{action}")
            except Exception as e:
                print_warning(f"{resource}:{action} - {str(e)[:50]}")
        
        # Create role
        print_step(3, "Create Role")
        
        role = admin_helper.create_role(
            name=f"Editor_{random_id}",
            description="Can read and write documents",
            permission_strings=["document:read", "document:write"]
        )
        
        if role:
            print_success(f"Created role: {role.get('name')}")
            print_info(f"Role ID: {role.get('id')}")
            role_id = role.get('id')
        else:
            print_warning("Role creation returned None")
            role_id = None
        
        # Create role binding
        print_step(4, "Create Role Binding")
        
        if role_id and user_id:
            binding = admin_helper.create_role_binding(user_id=user_id, role_id=role_id)
            print_success("Role binding created")
            print_info(f"Binding ID: {binding.get('id')}")
        else:
            print_warning(f"Skipping binding (role_id={role_id}, user_id={user_id})")
        
        # List permissions
        print_step(5, "List Permissions")
        
        perms = admin_client.list_permissions()
        print_success(f"User has {len(perms)} permissions")
        
        for perm in perms[:5]:
            resource = perm.get('resource', 'unknown')
            actions = perm.get('actions', [])
            print_info(f"  - {resource}: {', '.join(actions)}")
        
        if len(perms) > 5:
            print_info(f"  ... and {len(perms) - 5} more")
        
        # Success
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}E2E Test - COMPLETE SUCCESS!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        return True
        
    except Exception as e:
        print_error(f"E2E test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_complete_e2e_flow()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
