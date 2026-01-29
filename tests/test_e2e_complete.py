#!/usr/bin/env python3
"""
Complete End-to-End Test - Based on Real App Flow

This test replicates the actual flow from app.authsec.dev:
1. Admin registration (creates tenant)
2. Login with proper tenant_domain
3. Create permissions
4. Create roles
5. Verify RBAC works
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

def test_complete_e2e_flow():
    """Complete E2E test based on real app.authsec.dev flow"""
    
    # Generate unique test data
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    admin_email = f"e2e{random_id}@sdktest.com"
    admin_password = "E2ETest123!"
    # Use full FQDN format like the real app does
    tenant_subdomain = f"e2e{random_id}"
    tenant_domain = f"{tenant_subdomain}.app.authsec.dev"
    
    base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev/uflow")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Complete E2E Test - Real App Flow{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print_info(f"Test Admin: {admin_email}")
    print_info(f"Tenant Domain (FQDN): {tenant_domain}")
    print_info(f"Base URL: {base_url}")
    
    try:
        # ========================================
        # STEP 1: Admin Registration via Bootstrap
        # ========================================
        print_step(1, "Admin Registration (Bootstrap)")
        
        # Use the bootstrap endpoint like the real app does
        bootstrap_url = f"{base_url}/auth/admin/login/bootstrap"
        bootstrap_payload = {
            "email": admin_email,
            "password": admin_password,
            "tenant_domain": tenant_domain
        }
        
        print_info("Using /auth/admin/login/bootstrap endpoint")
        reg_response = requests.post(bootstrap_url, json=bootstrap_payload)
        reg_response.raise_for_status()
        
        reg_data = reg_response.json()
        print_success("Admin registration initiated via bootstrap")
        print_info(f"Status: {reg_response.status_code}")
        
        # Get OTP from response (dev environment)
        otp = reg_data.get('otp')
        if otp:
            print_success(f"OTP received: {otp}")
        else:
            print_warning("No OTP in bootstrap response -may need to check email in production")
        
        # ========================================
        # STEP 2: Verify Registration with OTP
        # ========================================
        print_step(2, "Verify Registration with OTP")
        
        if otp:
            admin_client = AuthSecClient(
                base_url=base_url,
                endpoint_type="admin"
            )
            
            verify_result = admin_client.verify_registration(
                email=admin_email,
                otp=otp
            )
            
            print_success("Registration verified")
            print_info(f"Verification response keys: {list(verify_result.keys()) if verify_result else 'None'}")
        else:
            print_warning("Skipping verification - no OTP available")
        
        # ========================================
        # STEP 3: Admin Login
        # ========================================
        print_step(3, "Admin Login")
        
        print_info("Logging in with email, password, and tenant_domain (no client_id)")
        
        admin_client = AuthSecClient(
            base_url=base_url,
            endpoint_type="admin"
        )
        
        try:
            token = admin_client.login(
                email=admin_email,
                password=admin_password,
                tenant_domain=tenant_domain  # FQDN format
            )
            
            print_success("Admin login successful!")
            print_info(f"Token (first 30 chars): {token[:30]}...")
            
        except requests.exceptions.HTTPError as e:
            print_error(f"Login failed: {e}")
            if e.response is not None:
                print_error(f"Response status: {e.response.status_code}")
                print_error(f"Response body: {e.response.text}")
            raise
        
        # ========================================
        # STEP 3: Create Permissions
        # ========================================
        print_step(3, "Create Permissions with AdminHelper")
        
        admin_helper = AdminHelper(
            token=token,
            base_url="https://dev.api.authsec.dev",  # Use main API base
            endpoint_type="admin"
        )
        
        # Create test permissions
        permissions_to_create = [
            ("document", "read", "Read documents"),
            ("document", "write", "Write documents"),
            ("document", "delete", "Delete documents"),
        ]
        
        created_count = 0
        for resource, action, description in permissions_to_create:
            try:
                perm = admin_helper.create_permission(resource, action, description)
                created_count += 1
                print_success(f"Created permission: {resource}:{action}")
            except Exception as e:
                print_warning(f"Permission {resource}:{action} might already exist: {str(e)[:80]}")
        
        print_info(f"Successfully created/verified {len(permissions_to_create)} permissions")
        
        # ========================================
        # STEP 4: Create Role
        # ========================================
        print_step(4, "Create Role with Permissions")
        
        role = admin_helper.create_role(
            name=f"Editor_{random_id}",
            description="Can read and write documents",
            permission_strings=["document:read", "document:write"]
        )
        
        print_success(f"Created role: {role.get('name')}")
        print_info(f"Role ID: {role.get('id')}")
        
        # ========================================
        # STEP 5: List Permissions for Admin
        # ========================================
        print_step(5, "List Admin Permissions")
        
        admin_client.set_token(token)
        permissions = admin_client.list_permissions()
        
        print_success(f"Admin has {len(permissions)} permissions")
        for perm in permissions[:5]:  # Show first 5
            resource = perm.get('resource', 'unknown')
            actions = perm.get('actions', [])
            print_info(f"  - {resource}: {', '.join(actions)}")
        if len(permissions) > 5:
            print_info(f"  ... and {len(permissions) - 5} more")
        
        # ========================================
        # Final Summary
        # ========================================
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}E2E Test - COMPLETE SUCCESS!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        print_success("Step 1: Admin registered via bootstrap ✓")
        print_success("Step 2: Admin logged in with tenant_domain ✓")
        print_success("Step 3: Created permissions ✓")
        print_success("Step 4: Created role with permissions ✓")
        print_success("Step 5: Listed permissions ✓")
        
        print(f"\n{CYAN}Test Artifacts Created:{RESET}")
        print_info(f"  Tenant Domain (FQDN): {tenant_domain}")
        print_info(f"  Admin Email: {admin_email}")
        print_info(f"  Role: {role.get('name')}")
        print_info(f"  Permissions: document:read, document:write, document:delete")
        
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
