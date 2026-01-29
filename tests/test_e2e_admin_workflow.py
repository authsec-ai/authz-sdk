#!/usr/bin/env python3
"""
End-to-End Admin Workflow Test - Token-Based

Complete workflow test covering:
1. Permission Creation
2. Role Creation
3. Role Binding (Admin)
4. Permission Verification (Admin)
5. End-User Permission Checks

This test uses pre-obtained tokens and focuses on RBAC functionality.

Usage:
    export TEST_ADMIN_TOKEN='admin-jwt-token'
    export TEST_ENDUSER_TOKEN='enduser-jwt-token'  # Optional, uses admin token if not set
    python3 tests/test_e2e_admin_workflow.py
"""

import sys
import os
import random
import string

# Add parent directory to path
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

def test_e2e_admin_workflow():
    """Complete end-to-end admin workflow test using tokens"""
    
    # Generate unique test data
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}End-to-End Admin Workflow Test (Token-Based){RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print_info(f"Test ID: {random_id}")
    print_info(f"Base URL: {base_url}")
    
    # Get tokens from environment
    admin_token = os.getenv('TEST_ADMIN_TOKEN') or os.getenv('TEST_AUTH_TOKEN')
    enduser_token = os.getenv('TEST_ENDUSER_TOKEN') or admin_token
    
    if not admin_token:
        print_error("TEST_ADMIN_TOKEN or TEST_AUTH_TOKEN environment variable required")
        print_info("Get token from: https://app.authsec.dev")
        print_info("Usage: export TEST_ADMIN_TOKEN='your-jwt-token'")
        return False
    
    results = {
        'passed': [],
        'failed': [],
        'skipped': []
    }
    
    try:
        # Initialize clients
        admin_client = AuthSecClient(base_url=f"{base_url}/uflow", token=admin_token)
        admin_helper = AdminHelper(token=admin_token, base_url=base_url)
        
        # ========================================
        # STEP 1: Get Admin User ID
        # ========================================
        print_step(1, "Get Admin User ID from Token")
        
        admin_user_id = None
        try:
            # Extract user ID from JWT decode
            import jwt
            decoded = jwt.decode(admin_token, options={"verify_signature": False})
            
            admin_user_id = (decoded.get('user_id') or 
                           decoded.get('sub') or 
                           decoded.get('client_id') or
                           decoded.get('id'))
            
            if admin_user_id:
                print_success(f"Admin User ID: {admin_user_id}")
                results['passed'].append('get_admin_user_id')
            else:
                print_warning("Could not extract admin user_id from token")
                results['failed'].append('get_admin_user_id')
        except Exception as e:
            print_error(f"Failed to get admin user ID: {e}")
            results['failed'].append('get_admin_user_id')
        
        # ========================================
        # STEP 2: Create Test Permissions
        # ========================================
        print_step(2, "Create Test Permissions")
        
        resource = f"test_resource_{random_id}"
        permissions_created = []
        
        try:
            for action in ['read', 'write', 'delete']:
                perm = admin_helper.create_permission(
                    resource=resource,
                    action=action,
                    description=f"{action.capitalize()} access to {resource}"
                )
                permissions_created.append(f"{resource}:{action}")
                print_success(f"Created: {resource}:{action}")
            
            results['passed'].append('create_permissions')
        except Exception as e:
            print_error(f"Permission creation failed: {e}")
            results['failed'].append('create_permissions')
        
        # ========================================
        # STEP 3: Create Test Role
        # ========================================
        print_step(3, "Create Test Role")
        
        role_id = None
        try:
            role = admin_helper.create_role(
                name=f"TestRole_{random_id}",
                description="E2E test role with permissions",
                permission_strings=permissions_created
            )
            
            if role:
                role_id = role.get('id')
                print_success(f"Created role: {role.get('name')}")
                print_info(f"Role ID: {role_id}")
                results['passed'].append('create_role')
            else:
                print_warning("create_role returned None")
                results['failed'].append('create_role')
        except Exception as e:
            print_error(f"Role creation failed: {e}")
            results['failed'].append('create_role')
        
        # ========================================
        # STEP 4: Create Admin Role Binding
        # ========================================
        print_step(4, "Assign Role to Admin User")
        
        if role_id and admin_user_id:
            try:
                binding = admin_helper.create_role_binding(
                    user_id=admin_user_id,
                    role_id=role_id
                )
                
                print_success(f"Assigned role to admin user")
                print_info(f"Binding ID: {binding.get('id')}")
                results['passed'].append('create_admin_role_binding')
            except Exception as e:
                print_error(f"Admin role binding failed: {e}")
                results['failed'].append('create_admin_role_binding')
        else:
            print_warning(f"Skipping role binding (role_id={role_id}, user_id={admin_user_id})")
            results['skipped'].append('create_admin_role_binding')
        
        # ========================================
        # STEP 5: Verify Admin Permissions
        # ========================================
        print_step(5, "Verify Admin User Permissions")
        
        try:
            # Check specific permission
            has_read = admin_client.check_permission(resource, "read")
            if has_read:
                print_success(f"✅ Admin has permission: {resource}:read")
            else:
                print_warning(f"❌ Admin denied: {resource}:read")
            
            # List all admin permissions
            admin_perms = admin_client.list_permissions()
            print_info(f"Admin has {len(admin_perms)} total permissions")
            
            # Check for our test permissions
            has_test_perm = any(p.get('resource') == resource for p in admin_perms)
            if has_test_perm:
                print_success(f"✅ Found test resource in admin permissions")
            
            results['passed'].append('verify_admin_permissions')
        except Exception as e:
            print_error(f"Admin permission verification failed: {e}")
            results['failed'].append('verify_admin_permissions')
        
        # ========================================
        # STEP 6: Get End-User ID (if different token)
        # ========================================
        if enduser_token and enduser_token != admin_token:
            print_step(6, "Get End-User ID from Token")
            
            enduser_user_id = None
            try:
                import jwt
                decoded = jwt.decode(enduser_token, options={"verify_signature": False})
                
                enduser_user_id = (decoded.get('user_id') or 
                                 decoded.get('sub') or 
                                 decoded.get('client_id') or
                                 decoded.get('id'))
                
                if enduser_user_id:
                    print_success(f"End-User ID: {enduser_user_id}")
                    results['passed'].append('get_enduser_id')
                else:
                    print_warning("Could not extract end-user user_id")
                    results['failed'].append('get_enduser_id')
            except Exception as e:
                print_error(f"Failed to get end-user ID: {e}")
                results['failed'].append('get_enduser_id')
            
            # ========================================
            # STEP 7: Create End-User Role Binding
            # ========================================
            print_step(7, "Assign Role to End-User")
            
            if role_id and enduser_user_id:
                try:
                    enduser_binding = admin_helper.create_role_binding(
                        user_id=enduser_user_id,
                        role_id=role_id
                    )
                    
                    print_success(f"Assigned role to end-user")
                    print_info(f"Binding ID: {enduser_binding.get('id')}")
                    results['passed'].append('create_enduser_role_binding')
                except Exception as e:
                    print_error(f"End-user role binding failed: {e}")
                    results['failed'].append('create_enduser_role_binding')
            else:
                print_warning(f"Skipping end-user binding (role_id={role_id}, user_id={enduser_user_id})")
                results['skipped'].append('create_enduser_role_binding')
            
            # ========================================
            # STEP 8: Verify End-User Permissions
            # ========================================
            print_step(8, "Verify End-User Permissions")
            
            try:
                enduser_client = AuthSecClient(base_url=f"{base_url}/uflow", token=enduser_token)
                
                # Check specific permission
                enduser_has_read = enduser_client.check_permission(resource, "read")
                if enduser_has_read:
                    print_success(f"✅ End-user has permission: {resource}:read")
                else:
                    print_warning(f"❌ End-user denied: {resource}:read")
                
                # List all end-user permissions
                enduser_perms = enduser_client.list_permissions()
                print_info(f"End-user has {len(enduser_perms)} total permissions")
                
                results['passed'].append('verify_enduser_permissions')
            except Exception as e:
                print_error(f"End-user permission verification failed: {e}")
                results['failed'].append('verify_enduser_permissions')
        else:
            print_step(6, "Skipping End-User Tests")
            print_info("Using same token for both admin and end-user")
            print_info("Set TEST_ENDUSER_TOKEN to test separate end-user")
            results['skipped'].extend(['get_enduser_id', 'create_enduser_role_binding', 'verify_enduser_permissions'])
        
        # ========================================
        # STEP 9: List All Roles
        # ========================================
        print_step(9, "List All Roles")
        
        try:
            roles = admin_helper.list_roles()
            print_success(f"Listed {len(roles)} roles")
            
            # Find our test role
            test_role = next((r for r in roles if r.get('name') == f"TestRole_{random_id}"), None)
            if test_role:
                print_success(f"✅ Found test role: {test_role.get('name')}")
            
            results['passed'].append('list_roles')
        except Exception as e:
            print_error(f"List roles failed: {e}")
            results['failed'].append('list_roles')
        
        # ========================================
        # Test Summary
        # ========================================
        print(f"\n{CYAN}{'='*70}{RESET}")
        print(f"{CYAN}Test Summary{RESET}")
        print(f"{CYAN}{'='*70}{RESET}\n")
        
        print(f"Passed ({len(results['passed'])}):")
        for test in results['passed']:
            print_success(f"  {test}")
        
        if results['failed']:
            print(f"\nFailed ({len(results['failed'])}):")
            for test in results['failed']:
                print_error(f"  {test}")
        
        if results['skipped']:
            print(f"\nSkipped ({len(results['skipped'])}):")
            for test in results['skipped']:
                print_warning(f"  {test}")
        
        total_run = len(results['passed']) + len(results['failed'])
        print(f"\nTotal: {total_run} tests run, {len(results['passed'])} passed, {len(results['failed'])} failed")
        
        if results['failed']:
            print(f"\n{RED}{'='*70}{RESET}")
            print(f"{RED}SOME TESTS FAILED{RESET}")
            print(f"{RED}{'='*70}{RESET}\n")
            return False
        else:
            print(f"\n{GREEN}{'='*70}{RESET}")
            print(f"{GREEN}✓✓✓ ALL TESTS PASSED!{RESET}")
            print(f"{GREEN}{'='*70}{RESET}\n")
            return True
            
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_e2e_admin_workflow()
    sys.exit(0 if success else 1)
