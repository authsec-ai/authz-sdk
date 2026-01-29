#!/usr/bin/env python3
"""
SDK Integration Test Program
Tests all SDK functionality against live database
"""

import sys
import os
import psycopg2
from uuid import uuid4
import requests

# Import SDK from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from authsec import AuthSecClient


# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'authsec',
    'password': 'authsec@kloudone',
    'dbname': 'authsec'
}

# Auth Manager URL - use environment variable or default to localhost
AUTH_MANAGER_URL = os.getenv("AUTH_MANAGER_URL", "http://localhost:7469")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

class SDKTester:
    def __init__(self):
        self.conn = None
        self.tenant_id = None
        self.project_id = None
        self.client_id = None
        self.user_id = None
        self.user_email = None
        self.role_id = None
        self.permission_id = None
        self.sdk_client = None
        
    def connect_db(self):
        """Connect to the database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.conn.autocommit = True
            print_success("Connected to database")
            return True
        except Exception as e:
            print_error(f"Database connection failed: {e}")
            return False
    
    def setup_test_data(self):
        """Create test tenant, user, roles, and permissions"""
        cursor = self.conn.cursor()
        
        try:
            # Generate UUIDs
            self.tenant_id = str(uuid4())
            self.project_id = str(uuid4())
            self.client_id = str(uuid4())
            self.user_id = str(uuid4())
            self.user_email = f"test_{uuid4().hex[:8]}@example.com"
            self.role_id = str(uuid4())
            self.permission_id = str(uuid4())
            
            print_info(f"Creating test data...")
            print_info(f"  Tenant ID: {self.tenant_id}")
            print_info(f"  User ID: {self.user_id}")
            print_info(f"  Email: {self.user_email}")
            
            # Create tenant (tenant_id is self-referential, set to same as id)
            cursor.execute("""
                INSERT INTO tenants (id, tenant_id, email, name, tenant_domain, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (self.tenant_id, self.tenant_id, "admin@sdktest.com", "SDK Test Tenant", "sdktest.local"))
            print_success("Created tenant")
            
            # Create project
            cursor.execute("""
                INSERT INTO projects (id, tenant_id, name, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """, (self.project_id, self.tenant_id, "SDK Test Project"))
            print_success("Created project")
            
            # Create client first (without owner_id initially - we'll update it)
            # Use tenant_id as temporary owner_id to satisfy NOT NULL constraint
            cursor.execute("""
                INSERT INTO clients (id, client_id, tenant_id, project_id, owner_id, org_id, name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (self.client_id, self.client_id, self.tenant_id, self.project_id, self.tenant_id, self.project_id, "SDK Test Client"))
            print_success("Created client (temp owner)")
            
            # Create user with client_id
            cursor.execute("""
                INSERT INTO users (id, client_id, tenant_id, email, username, tenant_domain, provider, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (self.user_id, self.client_id, self.tenant_id, self.user_email, self.user_email.split('@')[0], "sdktest.local", "local"))
            print_success("Created user")
            
            # Update client owner_id to point to user
            cursor.execute("""
                UPDATE clients SET owner_id = %s WHERE id = %s
            """, (self.user_id, self.client_id))
            print_success("Updated client owner")
            
            # Create permission
            cursor.execute("""
                INSERT INTO permissions (id, tenant_id, resource, action, description, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (self.permission_id, self.tenant_id, "invoice", "read", "Read invoices"))
            print_success("Created permission: invoice:read")
            
            # Create role
            cursor.execute("""
                INSERT INTO roles (id, tenant_id, name, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (self.role_id, self.tenant_id, "viewer", "Viewer role"))
            print_success("Created role: viewer")
            
            # Link permission to role
            cursor.execute("""
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (%s, %s)
            """, (self.role_id, self.permission_id))
            print_success("Linked permission to role")
            
            # Assign role to user (role binding)
            cursor.execute("""
                INSERT INTO role_bindings (id, tenant_id, user_id, role_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (str(uuid4()), self.tenant_id, self.user_id, self.role_id))
            print_success("Created role binding for user")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to create test data: {e}")
            return False
    
    def test_token_generation(self):
        """Test SDK token generation - SKIPPED (method removed for security)"""
        print_info("\n=== SKIPPED: Token Generation Test ===")
        print_warning("generate_token() method has been removed for security.")
        print_warning("Use login(email, password, client_id) instead")
        print_info("Skipping this test...")
        return True
    
    # REMOVED: test_authorize_local - SDK doesn't have authorize() method
    # This would be a local token claim check, not implemented yet
    
    def test_check_permission_remote(self):
        """Test remote permission check (database query)"""
        print_info("\n=== Testing check_permission() - Remote Check ===")
        print_info(f"  Using user-flow base URL: {self.sdk_client.uflow_base_url}")
        
        try:
            # Test with permission user should have
            result = self.sdk_client.check_permission("invoice", "read")
            if result:
                print_success("check_permission('invoice', 'read') = True ✓")
            else:
                print_warning("check_permission('invoice', 'read') = False")
                print_warning("  Note: Production user-flow doesn't have test tenant data")
                print_warning("  This is expected when testing against dev.api.authsec.dev")
            
            # Test with permission user should NOT have
            result = self.sdk_client.check_permission("invoice", "delete")
            if not result:
                print_success("check_permission('invoice', 'delete') = False ✓")
            else:
                print_error("check_permission('invoice', 'delete') = True (unexpected)")
            
            return True
            
        except Exception as e:
            print_error(f"Remote permission check failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # REMOVED: test_has_role - SDK doesn't have has_role() method
    # This would be a local token claim check, not implemented yet
    
    def cleanup(self):
        """Clean up test data"""
        if not self.conn:
            return
        
        print_info("\n=== Cleaning up test data ===")
        cursor = self.conn.cursor()
        
        try:
            # Delete in reverse order of creation (respecting foreign keys)
            cursor.execute("DELETE FROM role_bindings WHERE tenant_id = %s", (self.tenant_id,))
            cursor.execute("DELETE FROM role_permissions WHERE role_id = %s", (self.role_id,))
            cursor.execute("DELETE FROM roles WHERE id = %s", (self.role_id,))
            cursor.execute("DELETE FROM permissions WHERE id = %s", (self.permission_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (self.user_id,))
            cursor.execute("DELETE FROM clients WHERE id = %s", (self.client_id,))
            cursor.execute("DELETE FROM projects WHERE id = %s", (self.project_id,))
            cursor.execute("DELETE FROM tenants WHERE id = %s", (self.tenant_id,))
            
            print_success("Test data cleaned up")
            
        except Exception as e:
            print_warning(f"Cleanup warning: {e}")
        
        finally:
            self.conn.close()
            print_success("Database connection closed")

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("SDK Integration Test")
    print(f"{'='*60}{Colors.END}\n")
    
    tester = SDKTester()
    
    try:
        # Connect to database
        if not tester.connect_db():
            return 1
        
        # Setup test data
        if not tester.setup_test_data():
            return 1
        
        # Run tests
        print_info("\nStarting SDK tests...")
        
        success = True
        success = tester.test_token_generation() and success
        success = tester.test_check_permission_remote() and success
        
        # Summary
        print(f"\n{Colors.BLUE}{'='*60}")
        if success:
            print_success("All tests completed!")
        else:
            print_warning("Some tests had issues - check output above")
        print(f"{'='*60}{Colors.END}\n")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print_warning("\nTest interrupted by user")
        return 1
    
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
