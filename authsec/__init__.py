"""
AuthSec SDK for Python

Official Python SDK for AuthSec authentication and RBAC management.

Example:
    from authsec import AuthSecClient, AdminHelper
    
    # Authentication
    client = AuthSecClient("https://dev.api.authsec.dev")
    token = client.login("user@example.com", "password", "client-id")
    
    # RBAC Management
    admin = AdminHelper(token=token, endpoint_type="admin")
    role = admin.create_role("Editor", permission_strings=["document:read"])
"""

from .minimal import AuthSecClient
from .admin_helper import AdminHelper

__version__ = "1.0.0"
__all__ = ["AuthSecClient", "AdminHelper"]
