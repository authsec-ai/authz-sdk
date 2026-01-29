"""
Basic Authentication Example

This example demonstrates:
- Initializing the AuthSecClient with a token
- Checking permissions
- Making authenticated API requests

Note: Login requires OTP/MFA and must be done through https://app.authsec.dev
      Get your token from the dashboard and set it as an environment variable.
"""

from authsec import AuthSecClient
import os


def main():
    """Basic authentication workflow example"""
    
    # Get token from environment variable
    token = os.getenv('AUTHSEC_TOKEN')
    if not token:
        print("❌ Error: AUTHSEC_TOKEN environment variable not set")
        print("   Get your token from https://app.authsec.dev")
        print("   Then: export AUTHSEC_TOKEN='your-jwt-token'")
        return
    
    # Initialize the client with token
    print("🔧 Initializing AuthSec client with token...")
    client = AuthSecClient(
        base_url="https://dev.api.authsec.dev",
        token=token
    )
    print("✅ Client initialized!")
    
    # Check simple permissions
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
    print("\n📋 Listing all user permissions...")
    try:
        permissions = client.list_permissions()
        if permissions:
            for perm in permissions[:3]:  # Show first 3
                resource = perm.get('resource', 'unknown')
                actions = perm.get('actions', [])
                print(f"  - {resource}: {', '.join(actions)}")
            if len(permissions) > 3:
                print(f"  ... and {len(permissions) - 3} more")
        else:
            print("  No permissions found")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n✅ Example completed!")


def example_oidc_exchange():
    """Example of OIDC token exchange"""
    
    print("\n🔧 Example: OIDC Token Exchange")
    print("=" * 50)
    
    client = AuthSecClient("https://dev.api.authsec.dev")
    
    # Exchange OIDC token for application token
    oidc_token = os.getenv('OIDC_TOKEN', 'oidc-token-from-provider')
    
    try:
        app_token = client.exchange_oidc(oidc_token)
        print(f"✅ OIDC exchange successful! App token: {app_token[:20]}...")
        
        # Now use the app token
        client.set_token(app_token)
        permissions = client.list_permissions()
        print(f"   User has {len(permissions)} permissions")
    except Exception as e:
        print(f"❌ OIDC exchange failed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("AuthSec SDK - Basic Authentication Example")
    print("=" * 50)
    print()
    print("📌 Setup Required:")
    print("   1. Login at: https://app.authsec.dev")
    print("   2. Copy your JWT token")
    print("   3. Set: export AUTHSEC_TOKEN='your-token'")
    print()
    
    main()
    
    # Uncomment to run OIDC example:
    # example_oidc_exchange()
