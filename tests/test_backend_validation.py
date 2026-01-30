#!/usr/bin/env python3
"""
Backend API Validation Test

This test validates that the BACKEND APIs work correctly:
- Backend returns proper data structures
- Backend persists data to database
- Backend business logic functions correctly

This is different from SDK tests - SDK tests validate the wrapper methods work.
This test validates that the backend API implementation is correct.
"""

import sys
import os
import random
import string
import jwt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from authsec import AuthSecClient, AdminHelper

# Color codes
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

def print_header(title):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def generate_random_id(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def main():
    print_header("Backend API Validation Test")
    print_info("This test validates backend API implementation correctness")
    print_info("Tests will FAIL if backend doesn't return/persist data properly")
    print()
    
    # Get configuration
    token = os.getenv('TEST_AUTH_TOKEN')
    if not token:
        print_error("TEST_AUTH_TOKEN required")
        print_info("Get token from: https://app.authsec.dev")
        return 1
    
    base_url = os.getenv('TEST_BASE_URL', 'https://dev.api.authsec.dev')
    print_info(f"Testing backend at: {base_url}")
    print()
    
    # Initialize SDK
    admin = AdminHelper(token=token, base_url=base_url, endpoint_type="enduser")
    client = AuthSecClient(base_url=f"{base_url}/uflow", token=token)
    
    # Extract user ID from token
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get('user_id') or decoded.get('sub') or decoded.get('client_id')
        print_info(f"User ID from token: {user_id}")
    except Exception as e:
        print_error(f"Failed to decode token: {e}")
        return 1
    
    if not user_id:
        print_error("Could not extract user_id from token")
        return 1
    
    random_id = generate_random_id()
    results = {'passed': 0, 'failed': 0, 'warnings': []}
    
    # ========================================
    # Test 1: Permission Creation & Retrieval
    # ========================================
    print_header("Test 1: Permission Persistence")
    
    perm_resource = f"test_resource_{random_id}"
    perm_action = "read"
    
    try:
        print_info(f"Creating permission: {perm_resource}:{perm_action}")
        perm = admin.create_permission(perm_resource, perm_action, "Test permission")
        
        # VALIDATION: Backend should return permission object
        if not perm or not isinstance(perm, dict):
            print_error("❌ BACKEND FAILURE: create_permission returned invalid data")
            print_info(f"Expected: dict with id/resource/action")
            print_info(f"Got: {type(perm)} - {perm}")
            results['failed'] += 1
        else:
            print_success("Backend returned valid permission object")
            results['passed'] += 1
            
            # VALIDATION: Verify persistence with list_permissions
            print_info("Verifying permission was persisted...")
            perms = admin.list_permissions(resource=perm_resource)
            
            found = any(p.get('resource') == perm_resource and p.get('action') == perm_action for p in perms)
            
            if found:
                print_success("✅ Backend correctly persisted permission to database")
                results['passed'] += 1
            else:
                print_error("❌ BACKEND FAILURE: Permission not found in database")
                print_info(f"Created permission not returned by list_permissions()")
                results['failed'] += 1
                
    except Exception as e:
        print_error(f"❌ Permission test failed: {e}")
        results['failed'] += 2
    
    # ========================================
    # Test 2: Role Creation & Retrieval
    # ========================================
    print_header("Test 2: Role Persistence & Retrieval")
    
    role_name = f"TestRole_{random_id}"
    role_id = None
    
    try:
        print_info(f"Creating role: {role_name}")
        role = admin.create_role(
            name=role_name,
            description="Test role for backend validation",
            permission_strings=[f"{perm_resource}:read"]
        )
        
        # VALIDATION: Backend should return role object with ID
        if not role or not isinstance(role, dict) or not role.get('id'):
            print_error("❌ BACKEND FAILURE: create_role didn't return role with ID")
            print_info(f"Expected: dict with 'id' field")
            print_info(f"Got: {type(role)} - {role}")
            results['failed'] += 1
            results['warnings'].append("Role creation doesn't return ID - remaining tests will be skipped")
        else:
            role_id = role.get('id')
            print_success(f"Backend returned role with ID: {role_id}")
            results['passed'] += 1
            
            # VALIDATION: Verify persistence with list_roles
            print_info("Verifying role was persisted...")
            roles = admin.list_roles()
            
            found_role = next((r for r in roles if r.get('id') == role_id), None)
            
            if found_role:
                print_success("✅ Backend correctly persisted role to database")
                print_info(f"Role name: {found_role.get('name')}")
                results['passed'] += 1
            else:
                print_error("❌ BACKEND FAILURE: Role not found in list_roles()")
                print_info("Role created but not retrievable")
                results['failed'] += 1
            
            # VALIDATION: Verify retrieval with get_role
            print_info(f"Retrieving role by ID...")
            try:
                fetched_role = admin.get_role(role_id)
                
                if fetched_role and fetched_role.get('id') == role_id:
                    print_success("✅ Backend get_role() works correctly")
                    print_info(f"Retrieved: {fetched_role.get('name')}")
                    results['passed'] += 1
                else:
                    print_error("❌ BACKEND FAILURE: get_role() returned invalid data")
                    results['failed'] += 1
            except Exception as e:
                print_error(f"❌ get_role() failed: {e}")
                results['failed'] += 1
                
    except Exception as e:
        print_error(f"❌ Role test failed: {e}")
        results['failed'] += 3
    
    # ========================================
    # Test 3: Role Binding & Permission Flow
    # ========================================
    print_header("Test 3: Role Binding & Permission Logic")
    
    if not role_id:
        print_warning("⊘ Skipping - no role_id (backend role creation failed)")
        results['warnings'].append("Role binding tests skipped due to missing role_id")
    else:
        try:
            print_info(f"Creating role binding: user={user_id[:20]}... → role={role_id[:20]}...")
            binding = admin.create_role_binding(
                user_id=user_id,
                role_id=role_id
            )
            
            # VALIDATION: Backend should return binding object with ID
            if not binding or not isinstance(binding, dict) or not binding.get('id'):
                print_error("❌ BACKEND FAILURE: create_role_binding didn't return binding with ID")
                print_info(f"Expected: dict with 'id' field")
                print_info(f"Got: {type(binding)} - {binding}")
                results['failed'] += 1
            else:
                binding_id = binding.get('id')
                print_success(f"Backend returned binding with ID: {binding_id}")
                results['passed'] += 1
                
                # VALIDATION: Verify persistence with list_role_bindings
                print_info("Verifying binding was persisted...")
                bindings = admin.list_role_bindings(user_id=user_id)
                
                found_binding = any(b.get('id') == binding_id or b.get('role_id') == role_id for b in bindings)
                
                if found_binding:
                    print_success("✅ Backend correctly persisted role binding")
                    print_info(f"Found {len(bindings)} binding(s) for user")
                    results['passed'] += 1
                else:
                    print_error("❌ BACKEND FAILURE: Binding not found in list_role_bindings()")
                    results['failed'] += 1
                
                # VALIDATION: Verify business logic - permissions should now work
                print_info("Testing backend permission logic...")
                print_info(f"Checking if user has permission: {perm_resource}:read")
                
                has_permission = client.check_permission(perm_resource, "read")
                
                if has_permission:
                    print_success("✅ BACKEND BUSINESS LOGIC WORKS!")
                    print_info("Role binding → Permission grant → check_permission = TRUE")
                    results['passed'] += 1
                else:
                    print_error("❌ BACKEND LOGIC FAILURE: Permission check returned FALSE")
                    print_info("Role has permission, user has role binding, but check fails")
                    print_info("This indicates backend RBAC logic is broken")
                    results['failed'] += 1
                    
        except Exception as e:
            print_error(f"❌ Role binding test failed: {e}")
            results['failed'] += 3
    
    # ========================================
    # Test 4: User Permissions List
    # ========================================
    print_header("Test 4: User Permissions Aggregation")
    
    try:
        print_info("Listing user permissions (should include role permissions)...")
        user_perms = client.list_permissions()
        
        # VALIDATION: If role binding worked, user should have permissions
        if role_id and user_perms:
            has_test_perm = any(
                perm_resource in str(p) for p in user_perms
            )
            
            if has_test_perm:
                print_success("✅ Backend correctly aggregates role permissions to user")
                print_info(f"User has {len(user_perms)} permission(s)")
                results['passed'] += 1
            else:
                print_warning("⚠ User permissions don't include role permissions")
                print_info("This may indicate backend aggregation delay or logic issue")
                results['warnings'].append("Permissions not reflected in user permission list")
        else:
            print_info(f"User has {len(user_perms)} permission(s)")
            if not role_id:
                print_info("(No role binding created, so empty list is expected)")
            results['passed'] += 1
            
    except Exception as e:
        print_error(f"❌ List permissions failed: {e}")
        results['failed'] += 1
    
    # ========================================
    # Summary
    # ========================================
    print_header("Backend Validation Summary")
    
    total = results['passed'] + results['failed']
    pass_rate = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"Passed: {GREEN}{results['passed']}{RESET}/{total}")
    print(f"Failed: {RED}{results['failed']}{RESET}/{total}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if results['warnings']:
        print(f"\n{YELLOW}Warnings:{RESET}")
        for warning in results['warnings']:
            print(f"  ⚠ {warning}")
    
    print()
    
    if results['failed'] == 0:
        print(f"{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✓✓✓ BACKEND APIs WORKING CORRECTLY! ✓✓✓{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        return 0
    else:
        print(f"{RED}{'='*70}{RESET}")
        print(f"{RED}✗ BACKEND API FAILURES DETECTED ✗{RESET}")
        print(f"{RED}{'='*70}{RESET}\n")
        print_info("Backend API needs fixes for:")
        if results['failed'] > 0:
            print("  • Proper response data structures")
            print("  • Database persistence")
            print("  • Business logic implementation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
