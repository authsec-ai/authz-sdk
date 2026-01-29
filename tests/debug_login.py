#!/usr/bin/env python3
"""
Test complete register + OTP + login flow
"""
import requests
import json
import random
import string

base_url = "https://dev.api.authsec.dev"

# Generate random test user
random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
test_user = {
    "email": f"test{random_id}@sdktest.com",
    "name": f"Test User {random_id}",
    "password": "TestPassword123!",
    "tenant_domain": f"sdktest{random_id}"
}

print("="*70)
print("Testing Complete Registration Flow with OTP")
print("="*70)

try:
    # Step 1: Register
    print(f"\n1. Registering new user...")
    print(f"   Email: {test_user['email']}")
    print(f"   Tenant Domain: {test_user['tenant_domain']}")

    register_url = f"{base_url}/uflow/auth/admin/register"
    r = requests.post(register_url, json=test_user, timeout=10)
    print(f"   Status: {r.status_code}")
    
    if r.status_code in [200, 201]:
        register_data = r.json()
        print(f"   ✓ Registration initiated!")
        otp = register_data.get('otp')
        print(f"   OTP: {otp}")
        
        # Step 2: Verify OTP
        print(f"\n2. Verifying OTP...")
        verify_url = f"{base_url}/uflow/auth/admin/register/verify"
        verify_payload = {
            "email": test_user['email'],
            "otp": otp
        }
        
        r2 = requests.post(verify_url, json=verify_payload, timeout=10)
        print(f"   Status: {r2.status_code}")
        
        if r2.status_code == 200:
            verify_data = r2.json()
            print(f"   ✓ OTP verified!")
            print(f"   Response: {json.dumps(verify_data, indent=2)}")
            
            # Extract tenant_domain and client_id from verification response
            tenant_domain = verify_data.get('tenant_domain', test_user['tenant_domain'])
            client_id = verify_data.get('client_id')
            
            # Step 3: Login
            print(f"\n3. Logging in...")
            login_url = f"{base_url}/uflow/login"
            login_payload = {
                "email": test_user['email'],
                "password": test_user['password'],
                "client_id": client_id,
                "tenant_domain": tenant_domain
            }
            
            r3 = requests.post(login_url, json=login_payload, timeout=10)
            print(f"   Status: {r3.status_code}")
            
            if r3.status_code == 200:
                login_data = r3.json()
                print(f"   ✓ Login successful!")
                print(f"   Response keys: {list(login_data.keys())}")
                
                if 'token' in login_data:
                    print(f"\n   ✓✓✓ TOKEN RECEIVED!")
                    print(f"   Token (first 50 chars): {login_data['token'][:50]}...")
                    print(f"\n   Full Response:")
                    print(f"   {json.dumps(login_data, indent=2)}")
                else:
                    print(f"   Response: {json.dumps(login_data, indent=2)}")
            else:
                print(f"   ✗ Login failed")
                print(f"   Error: {r3.text}")
        else:
            print(f"   ✗ OTP verification failed")
            print(f"   Error: {r2.text}")
    else:
        print(f"   ✗ Registration failed")
        print(f"   Error: {r.text}")
        
except Exception as e:
    print(f"   ✗ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
