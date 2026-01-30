#!/usr/bin/env python3
"""
Quick debug script to test role creation
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from authsec import AdminHelper

token = os.getenv('TEST_AUTH_TOKEN')
if not token:
    print("❌ TEST_AUTH_TOKEN required")
    sys.exit(1)

base_url = os.getenv('TEST_BASE_URL', 'https://dev.api.authsec.dev')

admin = AdminHelper(token=token, base_url=base_url, endpoint_type="enduser")

print(f"Base URL: {base_url}")
print(f"Endpoint prefix: {admin.endpoint_prefix}")
print()

# Try to create role
print("Creating role...")
try:
    role = admin.create_role(
        name="DebugTestRole",
        description="Debug test",
        permission_strings=["test:read"]
    )
    print(f"Response: {role}")
    print(f"Type: {type(role)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("Listing roles...")
try:
    roles = admin.list_roles()
    print(f"Response: {roles}")
    print(f"Count: {len(roles)}")
    for r in roles[:5]:
        print(f"  - {r.get('name')}: {r.get('id')}")
except Exception as e:
    print(f"Error: {e}")
