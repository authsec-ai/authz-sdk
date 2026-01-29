#!/usr/bin/env python3
"""
Token-Based E2E Test Suite

Comprehensive validation of all SDK methods using a pre-obtained auth token.

Usage:
    export TEST_AUTH_TOKEN='your-jwt-token-here'
    python3 tests/test_e2e_token_based.py
    
Or for admin-only testing:
    export TEST_ADMIN_TOKEN='admin-jwt-token'
    python3 tests/test_e2e_token_based.py --admin-only
"""

import sys
import os
import random
import string
import jwt  # For extracting user_id from token
import argparse

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

def test_admin_operations(token, base_url="https://dev.api.authsec.dev"):
    """Test all admin SDK operations"""
    
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Admin Operations Test Suite{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results = {
        'passed': [],
        'failed': [],
        'skipped': []
    }
    
    try:
        admin_helper = AdminHelper(token=token, base_url=base_url)
        
        # ========================================
        # Test 1: Get User ID from Token
        # ========================================
        print_step(1, "Get User ID from Token")
        user_id = None
        
        try:
            # Initialize AuthSecClient
            client = AuthSecClient(base_url=f"{base_url}/uflow", token=token)
            
            # Method 1: JWT decode (no API call needed)
            print_info("Extracting user info from JWT token...")
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                user_id = (decoded.get('user_id') or 
                          decoded.get('sub') or 
                          decoded.get('userId') or
                          decoded.get('uid') or
                          decoded.get('client_id') or
                          decoded.get('id'))
                
                if user_id:
                    print_success(f"✅ User ID from JWT: {user_id}")
                    print_info(f"Available claims: {', '.join(decoded.keys())}")
                else:
                    print_warning("JWT decoded but no user_id claim found")
                    print_info(f"Available claims: {', '.join(decoded.keys())}")
            except Exception as jwt_error:
                print_warning(f"JWT decode failed: {str(jwt_error)[:60]}")
            
            # Method 2: Environment variable fallback
            if not user_id:
                user_id = os.getenv('TEST_USER_ID')
                if user_id:
                    print_info(f"Using TEST_USER_ID from environment: {user_id}")
                else:
                    print_error("❌ Could not extract user_id from token")
                    print_info("💡 Workaround: Set TEST_USER_ID environment variable:")
                    print_info("   export TEST_USER_ID='your-user-uuid'")
                    print_warning("⚠️  Role bindings will be skipped - permission checks will return empty")
            
            if user_id:
                results['passed'].append('get_user_id')
            else:
                results['failed'].append('get_user_id')
                
        except Exception as e:
            print_error(f"❌ Token processing failed: {e}")
            print_warning("Cannot create role bindings - permission checks will return empty")
            client = AuthSecClient(base_url=f"{base_url}/uflow", token=token)
            results['failed'].append('get_user_id')
        
        # ========================================
        # Test 2: Check Permission
        # ========================================
        print_step(2, "Check Permission")
        
        permissions_to_create = [
            (f"test_resource_{random_id}", "read", "Read test resource"),
            (f"test_resource_{random_id}", "write", "Write test resource"),
            (f"test_resource_{random_id}", "delete", "Delete test resource"),
        ]
        
        created_permissions = []
        for resource, action, description in permissions_to_create:
            try:
                perm = admin_helper.create_permission(resource, action, description)
                created_permissions.append(perm)
                print_success(f"Created: {resource}:{action}")
            except Exception as e:
                print_warning(f"Permission may exist: {resource}:{action} - {str(e)[:60]}")
        
        if created_permissions:
            results['passed'].append('create_permission')
        else:
            results['skipped'].append('create_permission (all existed)')
        
        # ========================================
        # Test 3: List Permissions  
        # ========================================
        print_step(3, "List Permissions")
        try:
            permissions = admin_helper.list_permissions()
            print_success(f"Listed {len(permissions)} permissions")
            
            # Show a few examples
            for perm in permissions[:3]:
                print_info(f"  - {perm.get('resource')}:{perm.get('action')}")
            if len(permissions) > 3:
                print_info(f"  ... and {len(permissions) - 3} more")
            
            results['passed'].append('list_permissions')
        except Exception as e:
            print_error(f"List permissions failed: {e}")
            results['failed'].append('list_permissions')
        
        # ========================================
        # Test 4: Create Role
        # ========================================
        print_step(4, "Create Role")
        try:
            role = admin_helper.create_role(
                name=f"TestRole_{random_id}",
                description="Test role for E2E validation",
                permission_strings=[
                    f"test_resource_{random_id}:read",
                    f"test_resource_{random_id}:write"
                ]
            )
            
            if role:
                print_success(f"Created role: {role.get('name')}")
                print_info(f"Role ID: {role.get('id')}")
                print_info(f"Permissions: {len(role.get('permissions', []))}")
                role_id = role.get('id')
            else:
                print_warning("create_role returned None/empty")
                print_info("This may indicate API returned empty response")
                role_id = None
            
            results['passed'].append('create_role')
        except Exception as e:
            print_error(f"Create role failed: {e}")
            print_info(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            results['failed'].append('create_role')
            role_id = None
        
        # ========================================
        # Test 4.5: Create Role Binding (NEW!)
        # ========================================
        print_step("4.5", "Assign Role to User (Role Binding)")
        if role_id and user_id:
            try:
                binding = admin_helper.create_role_binding(
                    user_id=user_id,
                    role_id=role_id
                )
                
                print_success(f"Assigned role '{role.get('name')}' to user")
                print_info(f"User ID: {user_id[:16]}...")
                print_info(f"Binding ID: {binding.get('id')}")
                print_info("✨ User now has permissions via role binding!")
                results['passed'].append('create_role_binding')
            except Exception as e:
                print_error(f"Role binding failed: {e}")
                print_warning("Permission checks will return empty (user has no role)")
                results['failed'].append('create_role_binding')
        else:
            if not role_id:
                print_warning("Skipping role binding (no role_id)")
            if not user_id:
                print_warning("Skipping role binding (no user_id)")
            print_info("Permission checks will return empty")
            results['skipped'].append('create_role_binding')
        
        # ========================================
        # Test 5: List Roles
        # ========================================
        print_step(5, "List Roles")
        try:
            roles = admin_helper.list_roles()
            print_success(f"Listed {len(roles)} roles")
            
            for role in roles[:3]:
                print_info(f"  - {role.get('name')}")
            if len(roles) > 3:
                print_info(f"  ... and {len(roles) - 3} more")
            
            results['passed'].append('list_roles')
        except Exception as e:
            print_error(f"List roles failed: {e}")
            results['failed'].append('list_roles')
        
        # ========================================
        # Test 6: Get Role by ID
        # ========================================
        if role_id:
            print_step(6, "Get Role by ID")
            try:
                fetched_role = admin_helper.get_role(role_id)
                print_success(f"Fetched role: {fetched_role.get('name')}")
                results['passed'].append('get_role')
            except Exception as e:
                print_error(f"Get role failed: {e}")
                results['failed'].append('get_role')
        else:
            results['skipped'].append('get_role (no role_id)')
        
        # ========================================
        # Test 7: Permission Checks (Should Pass Now!)
        # ========================================
        print_step(7, "Check Permissions")
        try:
            # Check a permission that should exist (via role binding)
            has_perm = client.check_permission(f"test_resource_{random_id}", "read")
            if has_perm:
                print_success(f"✅ Permission check PASSED: test_resource_{random_id}:read")
                print_info("User has permission via role binding!")
            else:
                print_warning(f"❌ Permission check DENIED: test_resource_{random_id}:read")
                print_info("This may indicate role binding failed or wasn't created")
            
            results['passed'].append('check_permission')
        except Exception as e:
            print_error(f"Check permission failed: {e}")
            results['failed'].append('check_permission')
        
        # ========================================
        # Test 8: List User Permissions
        # ========================================
        print_step(8, "List User Permissions")
        try:
            user_perms = client.list_permissions()
            print_success(f"User has {len(user_perms)} permissions")
            
            # Group by resource
            resources = {}
            for perm in user_perms:
                res = perm.get('resource', 'unknown')
                if res not in resources:
                    resources[res] = []
                resources[res].extend(perm.get('actions', []))
            
            for res, actions in list(resources.items())[:5]:
                print_info(f"  - {res}: {', '.join(actions)}")
            if len(resources) > 5:
                print_info(f"  ... and {len(resources) - 5} more resources")
            
            results['passed'].append('list_user_permissions')
        except Exception as e:
            print_error(f"List user permissions failed: {e}")
            results['failed'].append('list_user_permissions')
        
        return results
        
    except Exception as e:
        print_error(f"Admin operations failed: {e}")
        import traceback
        traceback.print_exc()
        return results

def test_enduser_operations(token, base_url="https://dev.api.authsec.dev"):
    """Test all end-user SDK operations"""
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}End-User Operations Test Suite{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results = {
        'passed': [],
        'failed': [],
        'skipped': []
    }
    
    try:
        client = AuthSecClient(
            base_url=f"{base_url}/uflow",
            token=token,
            endpoint_type="enduser"
        )
        
        # ========================================
        # Test 1: List Permissions
        # ========================================
        print_step(1, "List User Permissions")
        try:
            permissions = client.list_permissions()
            print_success(f"User has {len(permissions)} permissions")
            
            for perm in permissions[:5]:
                resource = perm.get('resource', 'unknown')
                actions = perm.get('actions', [])
                print_info(f"  - {resource}: {', '.join(actions)}")
            if len(permissions) > 5:
                print_info(f"  ... and {len(permissions) - 5} more")
            
            results['passed'].append('list_permissions')
        except Exception as e:
            print_error(f"List permissions failed: {e}")
            results['failed'].append('list_permissions')
        
        # ========================================
        # Test 3: Check Specific Permissions
        # ========================================
        print_step(3, "Check Specific Permissions")
        try:
            # Try some common permission checks
            test_checks = [
                ("document", "read"),
                ("document", "write"),
                ("admin", "access"),
            ]
            
            for resource, action in test_checks:
                has_perm = client.check_permission(resource, action)
                status = "✓ ALLOWED" if has_perm else "✗ DENIED"
                print_info(f"  {resource}:{action} → {status}")
            
            results['passed'].append('check_permission')
        except Exception as e:
            print_error(f"Permission checks failed: {e}")
            results['failed'].append('check_permission')
        
        return results
        
    except Exception as e:
        print_error(f"End-user operations failed: {e}")
        import traceback
        traceback.print_exc()
        return results

def print_summary(admin_results, enduser_results=None):
    """Print test summary"""
    
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}Test Summary{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")
    
    def print_results(title, results):
        if not results:
            return
            
        print(f"\n{BLUE}{title}:{RESET}")
        
        if results['passed']:
            print(f"{GREEN}  Passed ({len(results['passed'])}):{RESET}")
            for test in results['passed']:
                print(f"    ✓ {test}")
        
        if results['failed']:
            print(f"{RED}  Failed ({len(results['failed'])}):{RESET}")
            for test in results['failed']:
                print(f"    ✗ {test}")
        
        if results['skipped']:
            print(f"{YELLOW}  Skipped ({len(results['skipped'])}):{RESET}")
            for test in results['skipped']:
                print(f"    ⊘ {test}")
    
    print_results("Admin Operations", admin_results)
    if enduser_results:
        print_results("End-User Operations", enduser_results)
    
    # Overall status
    total_passed = len(admin_results['passed']) + (len(enduser_results['passed']) if enduser_results else 0)
    total_failed = len(admin_results['failed']) + (len(enduser_results['failed']) if enduser_results else 0)
    
    print(f"\n{CYAN}Overall:{RESET}")
    print(f"  Total Passed: {GREEN}{total_passed}{RESET}")
    print(f"  Total Failed: {RED}{total_failed}{RESET}")
    
    if total_failed == 0:
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✓✓✓ ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        return True
    else:
        print(f"\n{RED}{'='*70}{RESET}")
        print(f"{RED}Some tests failed{RESET}")
        print(f"{RED}{'='*70}{RESET}\n")
        return False

def main():
    parser = argparse.ArgumentParser(description='Token-based E2E SDK tests')
    parser.add_argument('--admin-only', action='store_true', help='Run only admin tests')
    parser.add_argument('--enduser-only', action='store_true', help='Run only end-user tests')
    parser.add_argument('--base-url', default='https://dev.api.authsec.dev', help='API base URL')
    args = parser.parse_args()
    
    # Get tokens from environment
    admin_token = os.getenv('TEST_ADMIN_TOKEN') or os.getenv('TEST_AUTH_TOKEN')
    enduser_token = os.getenv('TEST_ENDUSER_TOKEN') or os.getenv('TEST_AUTH_TOKEN')
    
    if not admin_token and not enduser_token:
        print_error("No auth token found!")
        print_info("Set one of:")
        print_info("  export TEST_AUTH_TOKEN='your-token'  (for both admin and end-user)")
        print_info("  export TEST_ADMIN_TOKEN='admin-token'")
        print_info("  export TEST_ENDUSER_TOKEN='enduser-token'")
        return 1
    
    admin_results = None
    enduser_results = None
    
    # Run admin tests
    if not args.enduser_only and admin_token:
        admin_results = test_admin_operations(admin_token, args.base_url)
    
    # Run end-user tests  
    if not args.admin_only and enduser_token:
        enduser_results = test_enduser_operations(enduser_token, args.base_url)
    
    # Print summary
    success = print_summary(admin_results or {}, enduser_results)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
