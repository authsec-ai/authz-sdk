#!/usr/bin/env python3
"""
Quick test to verify token and extract user_id

Usage:
    export TEST_AUTH_TOKEN='your-token'
    python3 tests/verify_token.py
"""

import os
import sys
import jwt
import json
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from authsec import AuthSecClient

def extract_user_id(token):
    """Try multiple methods to extract user_id from token"""
    
    print("🔍 Attempting to extract user_id from token...\n")
    
    # Method 1: Standard JWT decode
    print("Method 1: Standard JWT decode")
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get('user_id') or decoded.get('sub') or decoded.get('userId')
        
        print(f"✅ JWT decoded successfully")
        print(f"📋 Available claims: {', '.join(decoded.keys())}")
        
        if user_id:
            print(f"✅ User ID found: {user_id}\n")
            return user_id
        else:
            print(f"⚠️  No user_id/sub claim in token\n")
    except Exception as e:
        print(f"❌ JWT decode failed: {e}\n")
    
    # Method 2: Manual base64 decode
    print("Method 2: Manual base64 decode of JWT payload")
    try:
        parts = token.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded_bytes = base64.urlsafe_b64decode(payload)
            decoded = json.loads(decoded_bytes)
            
            user_id = decoded.get('user_id') or decoded.get('sub') or decoded.get('userId')
            
            print(f"✅ Manual decode successful")
            print(f"📋 Available claims: {', '.join(decoded.keys())}")
            
            if user_id:
                print(f"✅ User ID found: {user_id}\n")
                return user_id
            else:
                print(f"⚠️  No user_id/sub claim in token\n")
        else:
            print(f"❌ Token doesn't have 3 parts (header.payload.signature)\n")
    except Exception as e:
        print(f"❌ Manual decode failed: {e}\n")
    
    print("❌ Could not extract user_id from token")
    print("\n💡 Solution: Set TEST_USER_ID environment variable:")
    print("   export TEST_USER_ID='your-user-uuid-here'\n")
    
    return None

def main():
    token = os.getenv('TEST_AUTH_TOKEN')
    
    if not token:
        print("❌ Error: TEST_AUTH_TOKEN not set")
        print("   export TEST_AUTH_TOKEN='your-token-here'")
        sys.exit(1)
    
    print(f"Token length: {len(token)} characters")
    print(f"Token starts with: {token[:20]}...")
    print()
    
    user_id = extract_user_id(token)
    
    if user_id:
        print("="*60)
        print("✅ SUCCESS! Use this for role binding tests:")
        print(f"   export TEST_USER_ID='{user_id}'")
        print("="*60)
    else:
        print("="*60)
        print("❌ FAILED to extract user_id")
        print("   Manually set TEST_USER_ID environment variable")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
