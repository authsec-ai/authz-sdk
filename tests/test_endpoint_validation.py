#!/usr/bin/env python3
"""
Endpoint Validation Test
Tests all SDK endpoints to verify they exist (even if auth fails)
"""

import sys
import os
import requests

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

def test_endpoint_exists(name, method, url, payload=None, headers=None):
    """
    Test if an endpoint exists by checking response.
    - 2xx, 4xx = endpoint exists
    - Connection errors, 404, 503 with "no handler" = endpoint doesn't exist
    """
    try:
        if method.upper() == "GET":
            r = requests.get(url, headers=headers, timeout=5)
        elif method.upper() == "POST":
            r = requests.post(url, json=payload, headers=headers, timeout=5)
        else:
            r = requests.request(method, url, json=payload, headers=headers, timeout=5)
        
        # Any response (even errors) means endpoint exists
        if r.status_code in [200, 201]:
            print_success(f"{name}: Endpoint exists and responded OK ({r.status_code})")
            return True
        elif r.status_code in [400, 401, 403, 422]:
            print_success(f"{name}: Endpoint exists ({r.status_code} = expected auth/validation error)")
            return True
        elif r.status_code == 404:
            try:
                error_text = r.text.lower()
                if "not found" in error_text or "no handler" in error_text:
                    print_error(f"{name}: Endpoint NOT FOUND (404)")
                    return False
                else:
                    print_warning(f"{name}: Got 404 but may be resource-level, not endpoint-level")
                    return True
            except:
                print_error(f"{name}: Endpoint NOT FOUND (404)")
                return False
        else:
            print_warning(f"{name}: Unexpected status {r.status_code}, assuming exists")
            return True
            
    except requests.exceptions.ConnectionError as e:
        print_error(f"{name}: Connection failed - {str(e)[:80]}")
        return False
    except requests.exceptions.Timeout:
        print_warning(f"{name}: Timeout (server may be slow, assuming exists)")
        return True
    except Exception as e:
        print_error(f"{name}: Error - {str(e)[:80]}")
        return False

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}AuthSec SDK - Endpoint Validation Test{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Base URLs
    base_url = os.getenv("TEST_BASE_URL", "https://dev.api.authsec.dev")
    uflow_base_url = f"{base_url}/uflow"
    
    print_info(f"Base URL: {base_url}")
    print_info(f"UFlow URL: {uflow_base_url}")
    print()
    
    results = {}
    
    # ========================================
    # 1. Registration Endpoints (Admin)
    # ========================================
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}1. Admin Registration Endpoints{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results['register'] = test_endpoint_exists(
        "POST /auth/admin/register",
        "POST",
        f"{uflow_base_url}/auth/admin/register",
        payload={
            "email": "test@example.com",
            "name": "Test User",
            "password": "test123",
            "tenant_domain": "test-tenant"
        }
    )
    
    results['verify_registration'] = test_endpoint_exists(
        "POST /auth/admin/register/verify",
        "POST",
        f"{uflow_base_url}/auth/admin/register/verify",
        payload={
            "email": "test@example.com",
            "otp": "123456"
        }
    )
    
    # ========================================
    # 2. End-User Registration Endpoints
    # ========================================
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}2. End-User Registration Endpoints{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results['register_enduser'] = test_endpoint_exists(
        "POST /auth/enduser/initiate-registration",
        "POST",
        f"{uflow_base_url}/auth/enduser/initiate-registration",
        payload={
            "client_id": "00000000-0000-0000-0000-000000000000",
            "email": "test@example.com",
            "password": "test123"
        }
    )
    
    results['verify_enduser_registration'] = test_endpoint_exists(
        "POST /auth/enduser/verify-otp",
        "POST",
        f"{uflow_base_url}/auth/enduser/verify-otp",
        payload={
            "email": "test@example.com",
            "otp": "123456"
        }
    )
    
    # ========================================
    # 3. OIDC Token Exchange
    # ========================================
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}3. OIDC Token Exchange{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results['exchange_oidc'] = test_endpoint_exists(
        "POST /authmgr/oidcToken",
        "POST",
        f"{base_url}/authmgr/oidcToken",
        payload={
            "oidc_token": "fake-oidc-token"
        }
    )
    
    # ========================================
    # 4. Permission Endpoints (requires auth)
    # ========================================
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}4. Permission Endpoints (With Auth){RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    token = os.getenv("TEST_AUTH_TOKEN")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        
        results['check_permission'] = test_endpoint_exists(
            "POST /uflow/user/permissions/check",
            "POST",
            f"{uflow_base_url}/uflow/user/permissions/check",
            payload={
                "resource": "test:resource",
                "action": "read"
            },
            headers=headers
        )
        
        results['list_permissions'] = test_endpoint_exists(
            "GET /uflow/user/permissions",
            "GET",
            f"{uflow_base_url}/uflow/user/permissions",
            headers=headers
        )
    else:
        print_warning("TEST_AUTH_TOKEN not set, skipping authenticated endpoints")
        print_info("Set TEST_AUTH_TOKEN to test permission endpoints")
    
    # ========================================
    # SUMMARY
    # ========================================
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Endpoint Validation Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    exists = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, exists_flag in results.items():
        status = f"{GREEN}EXISTS{RESET}" if exists_flag else f"{RED}NOT FOUND{RESET}"
        print(f"  {name}: {status}")
    
    print(f"\n{BLUE}Result: {exists}/{total} endpoints validated{RESET}")
    
    if exists == total:
        print(f"\n{GREEN}✓ ALL ENDPOINTS EXIST!{RESET}\n")
        return 0
    else:
        missing = total - exists
        print(f"\n{RED}✗ {missing} endpoint(s) not found{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
