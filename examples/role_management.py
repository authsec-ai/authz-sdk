"""
Role Management Example

This example demonstrates:
- Assigning roles to users
- Listing role bindings
- Removing role bindings
- Working with scoped roles

Note: Get your token from https://app.authsec.dev first
"""

from authsec import AuthSecClient
import os


def main():
    """Role management workflow example"""
    
    # Get token from environment
    token = os.getenv('AUTHSEC_TOKEN')
    if not token:
        print("❌ Error: AUTHSEC_TOKEN environment variable not set")
        print("   Get your token from https://app.authsec.dev")
        print("   Then: export AUTHSEC_TOKEN='your-token'")
        return
    
    # Initialize with token
    print("🔧 Initializing AuthSec client...")
    client = AuthSecClient(
        base_url="https://dev.api.authsec.dev",
        token=token
    )
    print("✅ Client initialized!")
    
    # Example user and role IDs (replace with real IDs from your tenant)
    user_id = os.getenv('TEST_USER_ID', "550e8400-e29b-41d4-a716-446655440000")
    role_id = os.getenv('TEST_ROLE_ID', "660e8400-e29b-41d4-a716-446655440001")
    
    # Assign a role to a user (tenant-wide)
    print(f"\n👤 Assigning role {role_id[:8]}... to user {user_id[:8]}...")
    try:
        binding = client.assign_role(user_id, role_id)
        print(f"✅ Role assigned! Binding ID: {binding.get('id', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to assign role: {e}")
    
    # Assign a scoped role (project-specific)
    print(f"\n🎯 Assigning scoped role...")
    project_id = "770e8400-e29b-41d4-a716-446655440002"
    try:
        scoped_binding = client.assign_role(
            user_id,
            role_id,
            scope_type="project",
            scope_id=project_id
        )
        print(f"✅ Scoped role assigned! Binding ID: {scoped_binding.get('id', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to assign scoped role: {e}")
    
    # List all role bindings for the user
    print(f"\n📋 Listing role bindings for user {user_id[:8]}...")
    try:
        bindings = client.list_role_bindings(user_id=user_id)
        if bindings:
            for binding in bindings:
                scope_info = ""
                if binding.get('scope_type'):
                    scope_info = f" (scope: {binding.get('scope_type')})"
                print(f"  - Binding {binding.get('id', 'N/A')[:8]}...: "
                      f"Role {binding.get('role_name', 'Unknown')}{scope_info}")
        else:
            print("  No role bindings found")
    except Exception as e:
        print(f"❌ Failed to list bindings: {e}")
    
    # List role bindings by role
    print(f"\n📋 Listing all users with role {role_id[:8]}...")
    try:
        role_bindings = client.list_role_bindings(role_id=role_id)
        if role_bindings:
            for binding in role_bindings:
                print(f"  - User {binding.get('username', binding.get('user_id', 'Unknown')[:8])}")
        else:
            print("  No users found with this role")
    except Exception as e:
        print(f"❌ Failed to list role bindings: {e}")
    
    # Remove a role binding (example - uncomment to use)
    # print(f"\n🗑️  Removing role binding...")
    # binding_id = "880e8400-e29b-41d4-a716-446655440003"
    # try:
    #     success = client.remove_role_binding(binding_id)
    #     if success:
    #         print("✅ Role binding removed")
    # except Exception as e:
    #     print(f"❌ Failed to remove binding: {e}")
    
    print("\n✅ Example completed!")


def example_conditional_role_assignment():
    """Example of assigning a role with conditions"""
    
    print("\n🔧 Example: Conditional Role Assignment")
    print("=" * 50)
    
    token = os.getenv('AUTHSEC_TOKEN')
    client = AuthSecClient("https://dev.api.authsec.dev", token=token)
    
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    role_id = "660e8400-e29b-41d4-a716-446655440001"
    
    # Assign role with conditions (e.g., requires MFA)
    try:
        binding = client.assign_role(
            user_id,
            role_id,
            conditions={"mfa_required": True}
        )
        print("✅ Conditional role assigned - MFA required")
    except Exception as e:
        print(f"❌ Failed: {e}")


def example_admin_vs_user_endpoints():
    """Example showing admin vs user endpoints"""
    
    print("\n🔧 Example: Admin vs User Endpoints")
    print("=" * 50)
    
    token = os.getenv('AUTHSEC_TOKEN')
    client = AuthSecClient("https://dev.api.authsec.dev", token=token)
    
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    role_id = "660e8400-e29b-41d4-a716-446655440001"
    
    # Use user endpoint (default)
    print("Using user endpoint (/uflow/user/rbac/bindings):")
    try:
        binding1 = client.assign_role(user_id, role_id, admin=False)
        print(f"  ✅ Assigned via user endpoint")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    # Use admin endpoint (requires admin token)
    print("\nUsing admin endpoint (/uflow/admin/bindings):")
    try:
        binding2 = client.assign_role(user_id, role_id, admin=True)
        print(f"  ✅ Assigned via admin endpoint")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("AuthSec SDK - Role Management Example")
    print("=" * 50)
    print()
    print("📌 Setup Required:")
    print("   1. Login at: https://app.authsec.dev")
    print("   2. Copy your JWT token")
    print("   3. Set: export AUTHSEC_TOKEN='your-token'")
    print("   4. (Optional) Set TEST_USER_ID and TEST_ROLE_ID")
    print()
    
    main()
    
    # Uncomment to run other examples:
    # example_conditional_role_assignment()
    # example_admin_vs_user_endpoints()
