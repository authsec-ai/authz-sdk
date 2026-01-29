"""
AuthSec SDK for Python

Official Python SDK for AuthSec authentication and RBAC management.

Example:
    from authsec import AuthSecClient, AdminHelper
    import os
    
    # Authentication (get token from https://app.authsec.dev)
    client = AuthSecClient(
        base_url="https://dev.api.authsec.dev",
        token=os.getenv('AUTHSEC_TOKEN')
    )
    
    # RBAC Management
    admin = AdminHelper(token=os.getenv('AUTHSEC_ADMIN_TOKEN'), endpoint_type="admin")
    role = admin.create_role("Editor", permission_strings=["document:read"])
"""

from .minimal import AuthSecClient
from .admin_helper import AdminHelper

__version__ = "1.0.0"
__all__ = ["AuthSecClient", "AdminHelper"]
