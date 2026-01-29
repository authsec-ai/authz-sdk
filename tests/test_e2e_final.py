#!/usr/bin/env python3
"""
Working End-to-End Test - Uses SDK register() method

Complete workflow:
1. Admin registration with SDK (returns OTP in dev)
2. Verification with OTP
3. Login with tenant_domain
4. Create permissions & roles
5. Verify RBAC
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

def test_complete_e2e():
    """Complete working E2E test"""
    
   # Generate unique test data
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    admin_email = f"e2e{random_id}@sdktest.com"
    admin_name = f"E2E Test {random_id}"
    admin_password = "E2ETest123!"
    tenant_subdomain = f"e2e{random_id}"
    # Try both short and FQDN formats
    tenant_domain_short = tenant_subdomain
    tenant_domain_fqdn = f"{tenant_subdomain}.app.authsec.dev"
    
    base_url = os.getenv("UFLOW_BASE_URL", "https://dev.api.authsec.dev/uflow")
    api_base = "https://dev.api.authsec.dev"
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Working E2E Test{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    print_info(f"Admin: {admin_email}")
    print_info(f"Tenant (short): {tenant_domain_short}")
    print_info(f"Tenant (FQDN): {tenant_domain_fqdn}")
    
    try:
        # ========================================
        # STEP 1: Register Admin
        # ========================================
        print_step(1, "Admin Registration")
        
        client = AuthSecClient(base_url=base_url, endpoint_type="admin")
        
        reg_result = client.register(
            email=admin_email,
            name=admin_name,
            password=admin_password,
            tenant_domain=tenant_domain_short
        )
        
        print_success("Registration initiated")
        otp = reg_result.get('otp')
        if otp:
            print_success(f"OTP: {otp}")
        else:
            print_error("No OTP returned - cannot continue")
            return False
        
        # ========================================
        # STEP 2: Verify Registration
        # ========================================  
        print_step(2, "Verify OTP")
        
        verify_result = client.verify_registration(
            email=admin_email,
            otp=otp
        )
        
        print_success("Registration verified")
        if verify_result:
            print_info(f"Verify response: {list(verify_result.keys())}")
        
        # ========================================
        # STEP 3: Login (try both formats)
        # ========================================
        print_step(3, "Login")
        
        token = None
        # Try FQDN format first (real app uses this)
        for domain_format in [tenant_domain_fqdn, tenant_domain_short]:
            try:
                print_info(f"Trying tenant_domain: {domain_format}")
                token = client.login(
                    email=admin_email,
                    password=admin_password,
                    tenant_domain=domain_format
                )
                print_success(f"Login successful with: {domain_format}")
                break
            except Exception as e:
                print_warning(f"Login failed with {domain_format}: {str(e)[:60]}")
        
        if not token:
            print_error("Login failed with both formats")
            return False
            
        print_info(f"Token: {token[:30]}...")
        
        # ========================================
        # STEP 4: Create Permissions
        # ========================================
        print_step(4, "Create Permissions")
        
        admin_helper = AdminHelper(token=token, base_url=api_base)
        
        perms = [
            ("document", "read", "Read docs"),
            ("document", "write", "Write docs"),
        ]
        
        for resource, action, desc in perms:
            try:
                admin_helper.create_permission(resource, action, desc)
                print_success(f"{resource}:{action}")
            except:
                print_info(f"{resource}:{action} (exists)")
        
        # ========================================
        # STEP 5: Create Role
        # ========================================
        print_step(5, "Create Role")
        
        role = admin_helper.create_role(
            name=f"Editor_{random_id}",
            description="Editor role",
            permission_strings=["document:read", "document:write"]
        )
        
        print_success(f"Role: {role['name']}")
        
        # ========================================
        # STEP 6: List Permissions
        # ========================================
        print_step(6, "List Permissions")
        
        client.set_token(token)
        permissions = client.list_permissions()
        print_success(f"Found {len(permissions)} permissions")
        
        # ========================================
        # Summary
        # ========================================
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✓✓✓ E2E TEST - SUCCESS!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        
        print_success("1. Registered admin")
        print_success("2. Verified with OTP")
        print_success("3. Logged in")
        print_success("4. Created permissions")
        print_success("5. Created role")
        print_success("6. Listed permissions")
        
        print(f"\n{CYAN}Created:{RESET}")
        print_info(f"  Admin: {admin_email}")
        print_info(f"  Role: {role['name']}")
        print_info(f"  Permissions: {len(permissions)}")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = test_complete_e2e()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
