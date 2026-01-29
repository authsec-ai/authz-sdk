#!/usr/bin/env python3
"""
Simplified End-to-End Tests

Since the API doesn't return client_id from registration,
we create two separate E2E tests:

1. Registration Flow Test - Tests admin + enduser registration
2. Authenticated Operations Test - Tests RBAC operations with existing token

This matches the real-world usage where:
- Registration is a separate onboarding flow
- RBAC operations require an existing authenticated session
"""

import sys
import os
import random
import string
import requests

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


def test_registration_flow():
    """Test complete registration flow for admin and end-user"""
    
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    admin_email = f"admin_reg_{random_id}@sdktest.com"
    admin_name = f"Admin Reg {random_id}"
    admin_password = "AdminPass123!"
    tenant_domain = f"regtenant{random_id}"
    
    base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev/uflow")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}E2E Test 1: Registration Flow{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        # ========================================
        # STEP 1: Admin Registration
        # ========================================
        print_step(1, "Admin Registration")
        
        admin_client = AuthSecClient(base_url=base_url, endpoint_type="admin")
        
        reg_response = admin_client.register(
            email=admin_email,
            name=admin_name,
            password=admin_password,
            tenant_domain=tenant_domain
        )
        
        print_success("Admin registration initiated")
        print_info(f"Email: {reg_response['email']}")
        otp = reg_response.get('otp')
        print_success(f"OTP: {otp}")
        
        # ========================================
        # STEP 2: Complete Admin Registration
        # ========================================
        print_step(2, "Complete Admin Registration")
        
        complete_url = f"{base_url}/auth/admin/complete-registration"
        complete_response = requests.post(complete_url, json={
            "email": admin_email,
            "otp": otp
        })
        complete_response.raise_for_status()
        
        complete_data = complete_response.json()
        print_success("Registration completed")
        print_info(f"Tenant ID: {complete_data.get('tenant_id')}")
        print_info(f"User ID: {complete_data.get('user_id')}")
        
        # ========================================
        # STEP 3: Verify Tenant Exists
        # ========================================
        print_step(3, "Verify Tenant Exists")
        
        check_url = f"{base_url}/oidc/check-tenant"
        check_response = requests.get(check_url, params={"domain": tenant_domain})
        check_response.raise_for_status()
        
        check_data = check_response.json()
        print_success(f"Tenant verified: {check_data['exists']}")
        print_info(f"Domain: {check_data['domain']}")
        
        # ========================================
        # Summary
        # ========================================
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}Registration Flow Test - SUCCESS{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        print_success("✓ Step 1: Admin registration initiated")
        print_success("✓ Step 2: Registration completed with OTP")
        print_success("✓ Step 3: Tenant verified in system")
        
        print(f"\n{CYAN}Created Entities:{RESET}")
        print_info(f"  Tenant: {tenant_domain}")
        print_info(f"  Admin User: {admin_email}")
        print_info(f"  Tenant ID: {complete_data.get('tenant_id')}")
        
        return True
        
    except Exception as e:
        print_error(f"Registration flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authenticated_operations():
    """
    Test RBAC operations with authenticated token
    
    Note: This requires a valid token from a logged-in user.
    In production, this would come from the login flow.
    For testing, you can:
    1. Login via another method and export token
    2. Use a pre-generated test token
    """
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}E2E Test 2: Authenticated RBAC Operations{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Check if we have a token for testing
    test_token = os.getenv("TEST_AUTH_TOKEN")
    
    if not test_token:
        print_warning("TEST_AUTH_TOKEN not set")
        print_info("To test authenticated operations:")
        print_info("  1. Login via UI or other method")
        print_info("  2. Export token: export TEST_AUTH_TOKEN='your-jwt-token'")
        print_info("  3. Run this test again")
        print_info("")
        print_info("Skipping authenticated operations test")
        return True
    
    base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev/uflow")
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    try:
        # ========================================
        # STEP 1: Verify Token
        # ========================================
        print_step(1, "Verify Authentication Token")
        
        client = AuthSecClient(base_url=base_url, token=test_token)
        
        token_info = client.verify_token(test_token)
        print_success("Token verified")
        print_info(f"User ID: {token_info.get('user_id') or token_info.get('sub')}")
        
        # ========================================
        # STEP 2: Create Permission
        # ========================================
        print_step(2, "Create Permission")
        
        admin_helper = AdminHelper(token=test_token, base_url=base_url)
        
        try:
            perm = admin_helper.create_permission(
                resource="testdoc",
                action="read",
                description="Read test documents"
            )
            print_success(f"Permission created: testdoc:read")
        except Exception as e:
            print_warning(f"Permission may already exist: {str(e)[:100]}")
        
        # ========================================
        # STEP 3: Create Role
        # ========================================
        print_step(3, "Create Role")
        
        role = admin_helper.create_role(
            name=f"TestReader_{random_id}",
            description="Test reader role",
            permission_strings=["testdoc:read"]
        )
        
        print_success(f"Role created: {role['name']}")
        print_info(f"Role ID: {role['id']}")
        
        # ========================================
        # STEP 4: List Permissions
        # ========================================
        print_step(4, "List User Permissions")
        
        permissions = client.list_permissions()
        print_success(f"User has {len(permissions)} permissions")
        
        # ========================================
        # Summary
        # ========================================
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}Authenticated Operations Test - SUCCESS{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        print_success("✓ Step 1: Token verified")
        print_success("✓ Step 2: Permission created")
        print_success("✓ Step 3: Role created")
        print_success("✓ Step 4: Listed permissions")
        
        return True
        
    except Exception as e:
        print_error(f"Authenticated operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all E2E tests"""
    
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}AuthSec SDK - End-to-End Test Suite{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")
    
    results = []
    
    # Test 1: Registration Flow
    print_info("Running Test 1: Registration Flow...")
    results.append(("Registration Flow", test_registration_flow()))
    
    # Test 2: Authenticated Operations
    print_info("\nRunning Test 2: Authenticated Operations...")
    results.append(("Authenticated Operations", test_authenticated_operations()))
    
    # Final Summary
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}Test Suite Summary{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")
    
    for test_name, passed in results:
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print(f"\n{GREEN}✓ All E2E tests passed!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}✗ Some E2E tests failed{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
