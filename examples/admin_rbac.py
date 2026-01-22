"""
Admin Helper RBAC Management Example

This example demonstrates:
- Creating permissions
- Creating roles with permissions
- Managing role bindings
- Working with scopes
- Using both admin and enduser endpoints
"""

from authsec import AdminHelper


def main():
    """Complete RBAC management workflow"""
    
    # Initialize AdminHelper with enduser endpoint (default)
    print("🔧 Initializing AdminHelper (enduser endpoint)...")
    admin = AdminHelper(
        token="your-admin-token",
        base_url="https://dev.api.authsec.dev",
        endpoint_type="enduser",  # Uses tenant database
        debug=True  # Enable debug logging
    )
    
    # Step 1: Create permissions
    print("\n📝 Creating permissions...")
    try:
        perm1 = admin.create_permission(
            "document",
            "read",
            "Read documents"
        )
        print(f"  ✅ Created permission: document:read (ID: {perm1.get('id', 'N/A')[:8]}...)")
        
        perm2 = admin.create_permission(
            "document",
            "write",
            "Write documents"
        )
        print(f"  ✅ Created permission: document:write (ID: {perm2.get('id', 'N/A')[:8]}...)")
        
        perm3 = admin.create_permission(
            "document",
            "delete",
            "Delete documents"
        )
        print(f"  ✅ Created permission: document:delete (ID: {perm3.get('id', 'N/A')[:8]}...)")
    except Exception as e:
        print(f"  ⚠️  Permission creation failed (may already exist): {e}")
    
    # Step 2: List existing permissions
    print("\n📋 Listing all permissions...")
    try:
        permissions = admin.list_permissions()
        print(f"  Found {len(permissions)} permissions:")
        for perm in permissions[:5]:  # Show first 5
            print(f"    - {perm.get('resource')}:{perm.get('action')} "
                  f"(ID: {perm.get('id', 'N/A')[:8]}...)")
        if len(permissions) > 5:
            print(f"    ... and {len(permissions) - 5} more")
    except Exception as e:
        print(f"  ❌ Failed to list permissions: {e}")
    
    # Step 3: Create a role with permissions
    print("\n🎭 Creating roles...")
    try:
        editor_role = admin.create_role(
            name="Editor",
            description="Can read and write documents",
            permission_strings=["document:read", "document:write"]
        )
        print(f"  ✅ Created role: Editor (ID: {editor_role.get('id', 'N/A')[:8]}...)")
        
        viewer_role = admin.create_role(
            name="Viewer",
            description="Can only read documents",
            permission_strings=["document:read"]
        )
        print(f"  ✅ Created role: Viewer (ID: {viewer_role.get('id', 'N/A')[:8]}...)")
        
        admin_role = admin.create_role(
            name="Admin",
            description="Full access to documents",
            permission_strings=["document:read", "document:write", "document:delete"]
        )
        print(f"  ✅ Created role: Admin (ID: {admin_role.get('id', 'N/A')[:8]}...)")
    except Exception as e:
        print(f"  ❌ Failed to create roles: {e}")
        return
    
    # Step 4: List all roles
    print("\n📋 Listing all roles...")
    try:
        roles = admin.list_roles()
        print(f"  Found {len(roles)} roles:")
        for role in roles:
            print(f"    - {role.get('name')}: {role.get('description', 'No description')} "
                  f"({role.get('permissions_count', 0)} permissions)")
    except Exception as e:
        print(f"  ❌ Failed to list roles: {e}")
    
    # Step 5: Get specific role details
    print(f"\n🔍 Getting details for role '{editor_role.get('name')}'...")
    try:
        role_details = admin.get_role(editor_role['id'])
        print(f"  Name: {role_details.get('name')}")
        print(f"  Description: {role_details.get('description')}")
        print(f"  Permissions: {role_details.get('permissions_count')}")
    except Exception as e:
        print(f"  ❌ Failed to get role: {e}")
    
    # Step 6: Update a role
    print(f"\n✏️  Updating role '{editor_role.get('name')}'...")
    try:
        updated_role = admin.update_role(
            editor_role['id'],
            description="Can read, write, and delete documents",
            permission_strings=["document:read", "document:write", "document:delete"]
        )
        print(f"  ✅ Role updated: {updated_role.get('permissions_count')} permissions")
    except Exception as e:
        print(f"  ❌ Failed to update role: {e}")
    
    # Step 7: Create role bindings
    print("\n🔗 Creating role bindings...")
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    
    try:
        # Tenant-wide binding
        binding1 = admin.create_role_binding(
            user_id=user_id,
            role_id=viewer_role['id']
        )
        print(f"  ✅ Assigned Viewer role to user (tenant-wide)")
        
        # Project-scoped binding
        project_id = "770e8400-e29b-41d4-a716-446655440001"
        binding2 = admin.create_role_binding(
            user_id=user_id,
            role_id=editor_role['id'],
            scope_type="project",
            scope_id=project_id
        )
        print(f"  ✅ Assigned Editor role to user (project-scoped)")
    except Exception as e:
        print(f"  ❌ Failed to create bindings: {e}")
    
    # Step 8: List role bindings
    print(f"\n📋 Listing role bindings for user...")
    try:
        bindings = admin.list_role_bindings(user_id=user_id)
        print(f"  Found {len(bindings)} bindings:")
        for binding in bindings:
            scope = binding.get('scope_type', 'tenant-wide')
            print(f"    - {binding.get('role_name', 'Unknown')}: {scope}")
    except Exception as e:
        print(f"  ❌ Failed to list bindings: {e}")
    
    # Step 9: Create a scope
    print("\n🎯 Creating API scope...")
    try:
        scope = admin.create_scope(
            name="api.documents.write",
            description="Write access to documents API",
            resources=["document"]
        )
        print(f"  ✅ Created scope: {scope.get('name')}")
    except Exception as e:
        print(f"  ❌ Failed to create scope: {e}")
    
    # Step 10: List scopes
    print("\n📋 Listing all scopes...")
    try:
        scopes = admin.list_scopes()
        print(f"  Found {len(scopes)} scopes:")
        for scope in scopes[:3]:
            print(f"    - {scope.get('name')}: {scope.get('description', 'No description')}")
    except Exception as e:
        print(f"  ❌ Failed to list scopes: {e}")
    
    # Cleanup (commented out to avoid accidental deletion)
    # print("\n🗑️  Cleaning up...")
    # try:
    #     admin.remove_role_binding(binding1['id'])
    #     admin.remove_role_binding(binding2['id'])
    #     admin.delete_role(editor_role['id'])
    #     admin.delete_role(viewer_role['id'])
    #     admin.delete_role(admin_role['id'])
    #     print("  ✅ Cleanup completed")
    # except Exception as e:
    #     print(f"  ❌ Cleanup failed: {e}")
    
    print("\n✅ Example completed!")


def example_admin_endpoint():
    """Example using admin endpoint instead of enduser"""
    
    print("\n🔧 Example: Using Admin Endpoint")
    print("=" * 50)
    
    # Initialize with admin endpoint
    admin = AdminHelper(
        token="your-admin-token",
        base_url="https://dev.api.authsec.dev",
        endpoint_type="admin",  # Uses admin database
        debug=False
    )
    
    print("✅ AdminHelper initialized with admin endpoint")
    print("  Endpoint: /uflow/admin/*")
    print("  Database: Admin (platform-level)")
    
    # Operations work the same way, but target admin database
    try:
        roles = admin.list_roles()
        print(f"  Found {len(roles)} roles in admin database")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


def example_from_env():
    """Example using environment variables"""
    
    print("\n🔧 Example: Initialize from Environment Variables")
    print("=" * 50)
    
    # Set these environment variables:
    # export ADMIN_TOKEN="your-admin-token"
    # export ADMIN_BASE_URL="https://dev.api.authsec.dev"
    # export ENDPOINT_TYPE="enduser"  # or "admin"
    # export ADMIN_TIMEOUT="20"
    
    try:
        admin = AdminHelper.from_env(debug=True)
        print("✅ AdminHelper initialized from environment variables")
        
        roles = admin.list_roles()
        print(f"  Found {len(roles)} roles")
    except ValueError as e:
        print(f"❌ Environment variable error: {e}")
    except Exception as e:
        print(f"❌ Failed: {e}")


def example_batch_operations():
    """Example of batch RBAC operations"""
    
    print("\n🔧 Example: Batch Operations")
    print("=" * 50)
    
    admin = AdminHelper(token="your-admin-token")
    
    # Create multiple permissions at once
    print("Creating multiple permissions...")
    permissions_to_create = [
        ("user", "read", "Read users"),
        ("user", "write", "Write users"),
        ("user", "delete", "Delete users"),
        ("project", "read", "Read projects"),
        ("project", "write", "Write projects"),
    ]
    
    created_permissions = []
    for resource, action, description in permissions_to_create:
        try:
            perm = admin.create_permission(resource, action, description)
            created_permissions.append(perm)
            print(f"  ✅ {resource}:{action}")
        except Exception as e:
            print(f"  ⚠️  {resource}:{action} - {e}")
    
    print(f"\n✅ Created {len(created_permissions)} permissions")
    
    # Create role with all permissions
    print("\nCreating 'Super Admin' role...")
    try:
        role = admin.create_role(
            name="Super Admin",
            description="Full system access",
            permission_strings=[
                "user:read", "user:write", "user:delete",
                "project:read", "project:write"
            ]
        )
        print(f"  ✅ Role created with {role.get('permissions_count')} permissions")
    except Exception as e:
        print(f"  ❌ Failed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("AuthSec SDK - Admin Helper RBAC Example")
    print("=" * 50)
    
    # Note: This example requires a valid admin token
    # main()
    
    print("\n⚠️  This example requires a valid ADMIN_TOKEN")
    print("Set your token and uncomment main() to run")
    
    # Uncomment to run other examples:
    # example_admin_endpoint()
    # example_from_env()
    # example_batch_operations()
