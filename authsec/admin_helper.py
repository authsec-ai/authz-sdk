"""
Admin Helper SDK for AuthSec User Flow APIs

This SDK provides admin functions for managing RBAC resources (permissions, 
roles, scopes, bindings) and secrets via the User Flow end-user endpoints,
which operate on the tenant database.

Base URL: https://dev.api.authsec.dev (configurable)
"""

import requests
from typing import Optional, Dict, List, Any
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdminSDKError(Exception):
    """Base exception for Admin SDK"""
    pass


class PermissionError(AdminSDKError):
    """Permission-related errors"""
    pass


class RoleBindingError(AdminSDKError):
    """Role binding errors"""
    pass


class ScopeError(AdminSDKError):
    """Scope management errors"""
    pass


class SecretError(AdminSDKError):
    """Secret management errors"""
    pass


class AdminHelper:
    """Admin helper for managing RBAC and secrets via tenant database"""
    
    def __init__(
        self,
        token: str,
        base_url: str = "https://dev.api.authsec.dev",
        timeout: int = 10,
        debug: bool = False,
        endpoint_type: str = "enduser"
    ):
        """
        Initialize admin helper with authentication token.
        
        Args:
            token: JWT authentication token
            base_url: Base URL for API (default: https://dev.api.authsec.dev)
            timeout: Request timeout in seconds (default: 10)
            debug: Enable debug logging (default: False)
            endpoint_type: Endpoint type - 'admin' or 'enduser' (default: 'enduser')
                - 'enduser': Uses /uflow/enduser/* endpoints
                - 'admin': Uses /uflow/admin/* endpoints
        """
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.debug = debug
        
        # Validate and set endpoint type
        if endpoint_type not in ['admin', 'enduser']:
            raise ValueError(f"endpoint_type must be 'admin' or 'enduser', got '{endpoint_type}'")
        self.endpoint_type = endpoint_type
        if endpoint_type == 'enduser':
            self.endpoint_prefix = "/uflow/user/rbac"
        else:
            self.endpoint_prefix = f"/uflow/{endpoint_type}"
        
        if debug:
            logger.setLevel(logging.DEBUG)
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            AdminSDKError: On request failure
        """
        url = f"{self.base_url}{endpoint}"
        
        if self.debug:
            logger.debug(f"{method} {url}")
            if data:
                logger.debug(f"Body: {data}")
            if params:
                logger.debug(f"Params: {params}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response body: {response.text[:500]}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"{method} {endpoint} failed: {e}"
            if e.response is not None and e.response.content:
                try:
                    error_data = e.response.json()
                    error_msg = f"{error_msg} - {error_data.get('error', error_data)}"
                except:
                    error_msg = f"{error_msg} - {e.response.text}"
            raise AdminSDKError(error_msg)
        except requests.exceptions.RequestException as e:
            raise AdminSDKError(f"{method} {endpoint} failed: {e}")
    
    # ==================== Permission Management ====================
    
    def create_permission(
        self,
        resource: str,
        action: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a permission (resource + action).
        
        Args:
            resource: Resource name (e.g., "document", "user")
            action: Action name (e.g., "read", "write", "delete")
            description: Optional description
            
        Returns:
            Created permission data
            
        Raises:
            PermissionError: On creation failure
            
        Example:
            perm = admin.create_permission("document", "write", "Write documents")
        """
        data = {
            "resource": resource,
            "action": action
        }
        if description:
            data["description"] = description
        
        try:
            return self._make_request("POST", f"{self.endpoint_prefix}/permissions", data=data)
        except AdminSDKError as e:
            raise PermissionError(f"Failed to create permission: {e}")
    
    def list_permissions(self, resource: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all permissions.
        
        Args:
            resource: Filter by resource name (optional)
            
        Returns:
            List of permissions
            
        Example:
            perms = admin.list_permissions()
            doc_perms = admin.list_permissions(resource="document")
        """
        params = {}
        if resource:
            params["resource"] = resource
        
        try:
            response = self._make_request("GET", f"{self.endpoint_prefix}/permissions", params=params)
            return response if isinstance(response, list) else response.get("permissions", [])
        except AdminSDKError as e:
            raise PermissionError(f"Failed to list permissions: {e}")
    
    # ==================== Role Management ====================
    
    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        permission_ids: Optional[List[str]] = None,
        permission_strings: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new role with associated permissions.
        
        Args:
            name: Role name (required)
            description: Optional role description
            permission_ids: List of permission UUIDs to associate with role
            permission_strings: List of permission strings (format: "resource:action")
            
        Returns:
            Created role data with id, name, and permissions_count
            
        Raises:
            RoleBindingError: On creation failure
            
        Example:
            role = admin.create_role(
                "Editor",
                "Can edit documents",
                permission_strings=["document:read", "document:write"]
            )
        """
        data = {"name": name}
        if description:
            data["description"] = description
        if permission_ids:
            data["permission_ids"] = permission_ids
        if permission_strings:
            data["permission_strings"] = permission_strings
        
        try:
            return self._make_request("POST", f"{self.endpoint_prefix}/roles", data=data)
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to create role: {e}")
    
    def list_roles(
        self,
        resource: Optional[str] = None,
        role_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List roles with optional filters.
        
        Args:
            resource: Filter by resource name (optional)
            role_id: Filter by role ID (optional)
            user_id: Filter by user ID (optional)
            
        Returns:
            List of role objects with id, name, description, permissions_count, 
            users_assigned, user_ids, and usernames
            
        Examples:
            all_roles = admin.list_roles()
            doc_roles = admin.list_roles(resource="document")
            user_roles = admin.list_roles(user_id="user-uuid-123")
        """
        params = {}
        if resource:
            params["resource"] = resource
        if role_id:
            params["role_id"] = role_id
        if user_id:
            params["user_id"] = user_id
        
        try:
            response = self._make_request("GET", f"{self.endpoint_prefix}/roles", params=params)
            # Response is already a list from the backend
            return response if isinstance(response, list) else []
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to list roles: {e}")
    
    def get_role(self, role_id: str) -> Dict[str, Any]:
        """
        Get role details by ID.
        
        Args:
            role_id: Role UUID
            
        Returns:
            Role object with full details
            
        Raises:
            RoleBindingError: On retrieval failure
            
        Example:
            role = admin.get_role("role-uuid-123")
        """
        try:
            # Use list endpoint with filtering since /roles/{id} doesn't exist on RBAC endpoint
            params = {"role_id": role_id}
            response = self._make_request("GET", f"{self.endpoint_prefix}/roles", params=params)
            roles = response if isinstance(response, list) else response.get("roles", [])
            
            if roles and len(roles) > 0:
                return roles[0]
            raise RoleBindingError(f"Role not found: {role_id}")
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to get role: {e}")
    
    def update_role(
        self,
        role_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_ids: Optional[List[str]] = None,
        permission_strings: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing role.
        
        Args:
            role_id: Role UUID
            name: New role name (optional)
            description: New role description (optional)
            permission_ids: New list of permission UUIDs (replaces existing)
            permission_strings: New list of permission strings (replaces existing)
            
        Returns:
            Updated role data with id, name, and permissions_count
            
        Raises:
            RoleBindingError: On update failure
            
        Example:
            updated_role = admin.update_role(
                "role-uuid-123",
                name="Senior Editor",
                permission_strings=["document:read", "document:write", "document:delete"]
            )
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if permission_ids is not None:
            data["permission_ids"] = permission_ids
        if permission_strings is not None:
            data["permission_strings"] = permission_strings
        
        try:
            return self._make_request("PUT", f"{self.endpoint_prefix}/roles/{role_id}", data=data)
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to update role: {e}")
    
    def delete_role(self, role_id: str) -> bool:
        """
        Delete a role and all its permission mappings.
        
        Args:
            role_id: Role UUID
            
        Returns:
            True if successful
            
        Raises:
            RoleBindingError: On deletion failure
            
        Example:
            admin.delete_role("role-uuid-123")
        """
        try:
            self._make_request("DELETE", f"{self.endpoint_prefix}/roles/{role_id}")
            return True
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to delete role: {e}")
    
    # ==================== Role Binding Management ====================
    
    def create_role_binding(
        self,
        user_id: str,
        role_id: str,
        scope_type: Optional[str] = None,
        scope_id: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Bind a role to a user.
        
        Args:
            user_id: User UUID
            role_id: Role UUID
            scope_type: Scope type (e.g., "project", "organization") - None for tenant-wide
            scope_id: Scope ID (UUID) - None for tenant-wide
            conditions: Optional conditions (e.g., {"mfa_required": true})
            
        Returns:
            Created role binding data
            
        Raises:
            RoleBindingError: On creation failure
            
        Examples:
            # Tenant-wide binding
            binding = admin.create_role_binding(user_id, admin_role_id)
            
            # Project-scoped binding
            binding = admin.create_role_binding(
                user_id, editor_role_id,
                scope_type="project",
                scope_id=project_id
            )
        """
        data = {
            "user_id": user_id,
            "role_id": role_id
        }
        
        if scope_type or scope_id:
            data["scope"] = {
                "type": scope_type or "*",
                "id": scope_id or "*"
            }
        
        if conditions:
            data["conditions"] = conditions
        
        try:
            return self._make_request("POST", f"{self.endpoint_prefix}/bindings", data=data)
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to create role binding: {e}")
    
    def remove_role_binding(self, binding_id: str) -> bool:
        """
        Remove a role binding.
        
        Args:
            binding_id: Binding UUID
            
        Returns:
            True if successful
            
        Raises:
            RoleBindingError: On deletion failure
            
        Example:
            admin.remove_role_binding("binding-uuid-123")
        """
        try:
            self._make_request("DELETE", f"{self.endpoint_prefix}/bindings/{binding_id}")
            return True
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to remove role binding: {e}")
    
    def list_role_bindings(
        self,
        user_id: Optional[str] = None,
        role_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List role bindings.
        
        Args:
            user_id: Filter by user ID (optional)
            role_id: Filter by role ID (optional)
            
        Returns:
            List of role bindings
            
        Examples:
            all_bindings = admin.list_role_bindings()
            user_bindings = admin.list_role_bindings(user_id="user-uuid-123")
            role_bindings = admin.list_role_bindings(role_id="role-uuid-456")
        """
        params = {}
        if user_id:
            params["user_id"] = user_id
        if role_id:
            params["role_id"] = role_id
        
        try:
            response = self._make_request("GET", f"{self.endpoint_prefix}/bindings", params=params)
            return response if isinstance(response, list) else response.get("bindings", [])
        except AdminSDKError as e:
            raise RoleBindingError(f"Failed to list role bindings: {e}")
    
    # ==================== Scope Management ====================
    
    def create_scope(
        self,
        name: str,
        description: Optional[str] = None,
        resources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new OAuth/API scope.
        
        Args:
            name: Scope name (e.g., "api.documents.write")
            description: Optional description
            resources: Optional list of resource names
            
        Returns:
            Created scope data
            
        Raises:
            ScopeError: On creation failure
            
        Example:
            scope = admin.create_scope(
                "api.documents.write",
                "Write access to documents API",
                ["document"]
            )
        """
        data = {"name": name}
        if description:
            data["description"] = description
        if resources:
            data["resources"] = resources
        
        try:
            return self._make_request("POST", f"{self.endpoint_prefix}/scopes", data=data)
        except AdminSDKError as e:
            raise ScopeError(f"Failed to create scope: {e}")
    
    def list_scopes(self) -> List[Dict[str, Any]]:
        """
        List all scopes.
        
        Returns:
            List of scopes
            
        Example:
            scopes = admin.list_scopes()
        """
        try:
            response = self._make_request("GET", f"{self.endpoint_prefix}/scopes")
            return response if isinstance(response, list) else response.get("scopes", [])
        except AdminSDKError as e:
            raise ScopeError(f"Failed to list scopes: {e}")
    
    # ==================== Secret Management (External Service) ====================
    
    def create_secret(
        self,
        name: str,
        value: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a secret via external service.
        
        Args:
            name: Secret name
            value: Secret value
            metadata: Optional metadata
            
        Returns:
            Created secret data
            
        Raises:
            SecretError: On creation failure
            
        Example:
            secret = admin.create_secret(
                "api_key",
                "secret-value-here",
                {"environment": "production"}
            )
        """
        data = {
            "name": name,
            "value": value
        }
        if metadata:
            data["metadata"] = metadata
        
        try:
            # Note: Adjust endpoint when external-service URL is confirmed
            return self._make_request("POST", "/external-service/secrets", data=data)
        except AdminSDKError as e:
            raise SecretError(f"Failed to create secret: {e}")
    
    def list_secrets(self) -> List[Dict[str, Any]]:
        """
        List all secrets.
        
        Returns:
            List of secrets
            
        Example:
            secrets = admin.list_secrets()
        """
        try:
            response = self._make_request("GET", "/external-service/secrets")
            return response.get("secrets", [])
        except AdminSDKError as e:
            raise SecretError(f"Failed to list secrets: {e}")
    
    # ==================== Utility Methods ====================
    
    @classmethod
    def from_env(cls, debug: bool = False) -> "AdminHelper":
        """
        Create AdminHelper from environment variables.
        
        Environment variables:
            ADMIN_TOKEN: Authentication token
            ADMIN_BASE_URL: Base URL (default: https://dev.api.authsec.dev)
            ADMIN_TIMEOUT: Timeout in seconds (default: 10)
            ENDPOINT_TYPE: Endpoint type - 'admin' or 'enduser' (default: 'enduser')
            
        Args:
            debug: Enable debug logging
            
        Returns:
            AdminHelper instance
            
        Example:
            admin = AdminHelper.from_env()
            # Or for admin endpoints:
            # export ENDPOINT_TYPE=admin
            # admin = AdminHelper.from_env()
        """
        import os
        
        token = os.getenv("ADMIN_TOKEN")
        if not token:
            raise ValueError("ADMIN_TOKEN environment variable not set")
        
        return cls(
            token=token,
            base_url=os.getenv("ADMIN_BASE_URL", "https://dev.api.authsec.dev"),
            timeout=int(os.getenv("ADMIN_TIMEOUT", "10")),
            debug=debug,
            endpoint_type=os.getenv("ENDPOINT_TYPE", "enduser")
        )
