"""Minimal SDK client for AuthSec auth-manager."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import requests
import warnings


class AuthSecClient:
    """
    Minimal client for your server-side AuthN/AuthZ.
    - obtain a token (generateToken or oidcToken)
    - attach Authorization on outgoing requests
    - locally authorize resource+action from token claims
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        legacy_proxy_mode: bool = False,
        uflow_base_url: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Initialize AuthSec SDK client.
        
        Args:
            base_url: Base URL for auth-manager service
            timeout: Request timeout in seconds (default: 5.0)
            legacy_proxy_mode: Enable legacy proxy mode (default: False)
            uflow_base_url: Base URL for user-flow service (optional, defaults to base_url)
            token: Pre-authenticated JWT token (optional). If provided, skips login step.
                   Use this when you have already obtained a token via OIDC or other means.
        
        Example:
            >>> # Standard usage - will call login()
            >>> client = AuthSecClient("https://api.example.com")
            >>> client.login(email="user@example.com", password="pass", client_id="...")
            
            >>> # With pre-authenticated token
            >>> client = AuthSecClient("https://api.example.com", token="eyJhbG...")
            >>> # Ready to use immediately - no login() needed
        """
        self.base_url = base_url.rstrip("/")
        self.uflow_base_url = uflow_base_url.rstrip("/") if uflow_base_url else self.base_url
        self.timeout = timeout
        self.legacy_proxy_mode = legacy_proxy_mode
        self.token: Optional[str] = token  # Can be set during init or via login()
        self._claims_cache: Optional[Dict[str, Any]] = None

    def _get_path(self, endpoint: str) -> str:
        """Resolve path based on mode (Legacy Proxy vs Standard User API)"""
        if self.legacy_proxy_mode:
            # Map standard endpoints to legacy /authmgr paths
            if endpoint == "/auth/user/verifyToken":
                return "/authmgr/verifyToken"
            if endpoint == "/auth/user/generateToken":
                return "/authmgr/generateToken"
            if endpoint == "/auth/user/permissions/check":
                return "/authmgr/enduser/permissions/check"
            # Fallback (or add others as needed)
            return endpoint.replace("/auth/user/", "/authmgr/")
        return endpoint

    # ---------------------------
    # Token lifecycle (server calls)
    # ---------------------------

    def login(
        self,
        *,
        email: str,
        password: str,
        client_id: str,
        uflow_base_url: Optional[str] = None
    ) -> str:
        """
        Login with email and password to get JWT token.
        
        This is the RECOMMENDED method for end-user authentication.
        Uses the /uflow/auth/enduser/login endpoint.
        
        Args:
            email: User email address
            password: User password
            client_id: Client UUID
            uflow_base_url: User-flow base URL (optional, uses self.uflow_base_url if not provided)
        
        Returns:
            JWT access token
            
        Raises:
            HTTPError: If authentication fails (401/403)
            
        Example:
            >>> client = AuthSecClient("http://localhost:7468")
            >>> token = client.login(
            ...     email="user@example.com",
            ...     password="secure-password",
            ...     client_id="client-uuid-123"
            ... )
        """
        base = uflow_base_url or self.uflow_base_url
        url = f"{base}/auth/enduser/login"
        payload = {
            "email": email,
            "password": password,
            "client_id": client_id
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        
        response = r.json()
        tok = response.get("token")
        if not tok:
            raise ValueError("Login response did not contain token")
        
        self.set_token(tok)
        return tok
    
    def exchange_oidc(self, oidc_token: str) -> str:
        """Call /authmgr/oidcToken to exchange an OIDC token for application token."""
        url = f"{self.base_url}/authmgr/oidcToken"
        r = requests.post(url, json={"oidc_token": oidc_token}, timeout=self.timeout)
        r.raise_for_status()
        tok = r.json()["access_token"]
        self.set_token(tok)
        return tok

    def set_token(self, token: str) -> None:
        self.token = token
        self._claims_cache = None  # reset cache

    def verify_token(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Server-side authentication check: POST /authmgr/verifyToken
        Returns decoded claims if the token is valid.
        """
        tok = token or self.token
        if not tok:
            raise RuntimeError("No token available to verify. Set or pass a token.")
        url = f"{self.base_url}/authmgr/verifyToken"
        r = requests.post(url, json={"token": tok}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    # ---------------------------
    # Making app requests (token injection)
    # ---------------------------

    def request(self, method: str, url_or_path: str, **kwargs) -> requests.Response:
        """Injects Authorization: Bearer <token> and calls the app/backend."""
        if self.token is None:
            raise RuntimeError("No token set. Call login() or exchange_oidc() first.")
        headers = kwargs.pop("headers", {}) or {}
        headers.setdefault("Authorization", f"Bearer {self.token}")
        # support full URLs or relative paths
        if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
            url = f"{self.base_url.rstrip('/')}/{url_or_path.lstrip('/')}"
        else:
            url = url_or_path
        return requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)

    # ---------------------------
    # RBAC Permission Checks (Tenant DB)
    # ---------------------------

    def check_permission(self, resource: str, action: str) -> bool:
        """
        Check if user has permission for resource:action.
        Uses /uflow/user/permissions/check endpoint (queries tenant DB).
        """
        if not self.token:
            return False
        url = f"{self.uflow_base_url}/uflow/user/permissions/check"
        params = {"resource": resource, "action": action}
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            r = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            return r.json().get("allowed", False)
        except requests.RequestException:
            return False

    def check_permission_scoped(self, resource: str, action: str, scope_type: str, scope_id: str) -> bool:
        """
        Check if user has scoped permission for resource:action within a specific scope.
        
        This is useful for checking permissions within a specific context, such as:
        - Can user read documents in project X?
        - Can user write to organization Y?

        Args:
            resource: Resource name (e.g., "document", "user")
            action: Action name (e.g., "read", "write", "delete")
            scope_type: Type of scope (e.g., "project", "organization", "billing_account")
            scope_id: UUID of the scope entity

        Returns:
            True if user has scoped permission, False otherwise

        Example:
            client.check_permission_scoped("document", "write", "project", "123e4567-e89b-12d3-a456-426614174000")
        """
        if not self.token:
            return False
        url = f"{self.uflow_base_url}/uflow/user/permissions/check"
        params = {
            "resource": resource,
            "action": action,
            "scope": f"{scope_type}:{scope_id}"
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            r = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            return r.json().get("allowed", False)
        except requests.RequestException:
            return False


    def list_permissions(self) -> List[Dict[str, Any]]:
        """
        List all permissions for authenticated user.
        Uses /uflow/user/permissions endpoint (queries tenant DB).
        
        Returns:
            List of permission objects with resource and actions
        """
        if not self.token:
            return []
        url = f"{self.uflow_base_url}/uflow/user/permissions"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            r = requests.get(url, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            return r.json().get("permissions", [])
        except requests.RequestException:
            return []
    # ---------------------------
    # Admin: Role Management
    # ---------------------------

    def assign_role(
        self,
        user_id: str,
        role_id: str,
        scope_type: Optional[str] = None,
        scope_id: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None,
        admin: bool = False
    ) -> Dict[str, Any]:
        """
        Assign a role to a user (creates a role binding).
        Uses /uflow/user/rbac/bindings or /uflow/admin/bindings endpoint.
        
        Args:
            user_id: User UUID to assign the role to
            role_id: Role UUID to assign
            scope_type: Optional scope type (e.g., "project", "organization"). Use None or "*" for tenant-wide.
            scope_id: Optional scope ID (UUID). Use None or "*" for tenant-wide.
            conditions: Optional conditions dict (e.g., {"mfa_required": True})
            admin: If True, uses admin endpoint (/uflow/admin/bindings). Default: False (user endpoint)
            
        Returns:
            Dict with binding details: {"id": "...", "status": "active", "scope_description": "...", "role_name": "..."}
            
        Raises:
            RuntimeError: If no token is set or request fails
        """
        if not self.token:
            raise RuntimeError("No token set. Call login() or exchange_oidc() first.")
        
        # Determine endpoint based on admin flag
        endpoint = "/uflow/admin/bindings" if admin else "/uflow/user/rbac/bindings"
        url = f"{self.base_url}{endpoint}"
        
        # Build payload
        payload: Dict[str, Any] = {
            "user_id": user_id,
            "role_id": role_id
        }
        
        # Add scope if provided (use "*" for tenant-wide)
        if scope_type or scope_id:
            payload["scope"] = {
                "type": scope_type or "*",
                "id": scope_id or "*"
            }
        
        # Add conditions if provided
        if conditions:
            payload["conditions"] = conditions
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to assign role: {e}")

    def remove_role_binding(self, binding_id: str, admin: bool = False) -> bool:
        """
        Remove a role binding.
        
        Args:
            binding_id: Binding UUID to remove
            admin: If True, uses admin endpoint (/uflow/admin/bindings/{id}). Default: False (user endpoint)
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If no token is set or request fails
            
        Example:
            client.remove_role_binding("binding-uuid-123")
        """
        if not self.token:
            raise RuntimeError("No token set. Call login() or exchange_oidc() first.")
        
        # Determine endpoint based on admin flag
        endpoint = "/uflow/admin/bindings" if admin else "/uflow/user/rbac/bindings"
        url = f"{self.base_url}{endpoint}/{binding_id}"
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            r = requests.delete(url, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            return True
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to remove role binding: {e}")

    def list_role_bindings(
        self,
        user_id: Optional[str] = None,
        role_id: Optional[str] = None,
        scope_type: Optional[str] = None,
        admin: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List role bindings with optional filters.
        
        Args:
            user_id: Filter by user ID (optional)
            role_id: Filter by role ID (optional)
            scope_type: Filter by scope type (optional)
            admin: If True, uses admin endpoint. Default: False (user endpoint)
            
        Returns:
            List of role binding objects with id, user_id, username, role_id, role_name,
            scope_type, scope_id, conditions, created_at, and expires_at
            
        Raises:
            RuntimeError: If no token is set
            
        Examples:
            all_bindings = client.list_role_bindings()
            user_bindings = client.list_role_bindings(user_id="user-uuid-123")
            role_bindings = client.list_role_bindings(role_id="role-uuid-456", admin=True)
        """
        if not self.token:
            raise RuntimeError("No token set. Call login() or exchange_oidc() first.")
        
        # Determine endpoint based on admin flag
        endpoint = "/uflow/admin/bindings" if admin else "/uflow/user/rbac/bindings"
        url = f"{self.base_url}{endpoint}"
        
        params = {}
        if user_id:
            params["user_id"] = user_id
        if role_id:
            params["role_id"] = role_id
        if scope_type:
            params["scope_type"] = scope_type
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            r = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            r.raise_for_status()
            response = r.json()
            # Response should be a list from the backend
            return response if isinstance(response, list) else []
        except requests.RequestException:
            return []
