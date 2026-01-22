"""
Basic Authentication Example

This example demonstrates:
- Initializing the AuthSecClient
- Logging in with email and password
- Checking permissions
- Making authenticated API requests
"""

from authsec import AuthSecClient


def main():
    """Basic authentication workflow example"""
    
    # Initialize the client
    print("🔧 Initializing AuthSec client...")
    client = AuthSecClient("https://dev.api.authsec.dev")
    
    # Login with credentials
    print("\n🔐 Logging in...")
    try:
        token = client.login(
            email="user@example.com",
            password="your-password",
            client_id="your-client-id"
        )
        print(f"✅ Login successful! Token: {token[:20]}...")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Check a simple permission
    print("\n🔍 Checking permissions...")
    can_read = client.check_permission("document", "read")
    can_write = client.check_permission("document", "write")
    can_delete = client.check_permission("document", "delete")
    
    print(f"  Can read documents: {'✅' if can_read else '❌'}")
    print(f"  Can write documents: {'✅' if can_write else '❌'}")
    print(f"  Can delete documents: {'✅' if can_delete else '❌'}")
    
    # Check scoped permissions
    print("\n🎯 Checking scoped permissions...")
    project_id = "123e4567-e89b-12d3-a456-426614174000"
    can_write_in_project = client.check_permission_scoped(
        "document", "write", "project", project_id
    )
    print(f"  Can write in project {project_id[:8]}...: {'✅' if can_write_in_project else '❌'}")
    
    # List all permissions
    print("\n📋 Listing all permissions...")
    permissions = client.list_permissions()
    if permissions:
        for perm in permissions[:3]:  # Show first 3
            print(f"  - {perm.get('resource')}: {', '.join(perm.get('actions', []))}")
        if len(permissions) > 3:
            print(f"  ... and {len(permissions) - 3} more")
    else:
        print("  No permissions found")
    
    # Example of making an authenticated API request
    print("\n🌐 Making authenticated API request...")
    try:
        # This would call your backend API with the token
        # response = client.request("GET", "/api/documents")
        print("  Use client.request() to make authenticated API calls")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n✅ Example completed!")


def example_with_preauth_token():
    """Example using a pre-authenticated token"""
    
    print("\n🔧 Example: Using pre-authenticated token")
    print("=" * 50)
    
    # If you already have a token (e.g., from OIDC)
    existing_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    # Initialize client with token - no login needed
    client = AuthSecClient(
        "https://dev.api.authsec.dev",
        token=existing_token
    )
    
    print("✅ Client initialized with existing token")
    print("  Ready to check permissions immediately!")
    
    # Can now use the client without calling login()
    can_read = client.check_permission("document", "read")
    print(f"  Can read: {can_read}")


def example_oidc_exchange():
    """Example of OIDC token exchange"""
    
    print("\n🔧 Example: OIDC Token Exchange")
    print("=" * 50)
    
    client = AuthSecClient("https://dev.api.authsec.dev")
    
    # Exchange OIDC token for application token
    oidc_token = "oidc-token-from-provider"
    
    try:
        app_token = client.exchange_oidc(oidc_token)
        print(f"✅ OIDC exchange successful! App token: {app_token[:20]}...")
    except Exception as e:
        print(f"❌ OIDC exchange failed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("AuthSec SDK - Basic Authentication Example")
    print("=" * 50)
    
    main()
    
    # Uncomment to run other examples:
    # example_with_preauth_token()
    # example_oidc_exchange()
