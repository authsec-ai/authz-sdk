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
        token: Optional[str] = None,
        endpoint_type: str = "enduser"
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
            endpoint_type: Endpoint type to use - "admin" or "enduser" (default: "enduser")
                          This determines which API paths are used by default.
        
        Example:
            >>> # End-user client (default)
            >>> client = AuthSecClient("https://api.example.com")
            
            >>> # Admin client
            >>> admin = AuthSecClient("https://api.example.com", endpoint_type="admin")
            
            >>> # With pre-authenticated token
            >>> client = AuthSecClient("https://api.example.com", token="eyJhbG...")
        """
        self.base_url = base_url.rstrip("/")
        self.uflow_base_url = uflow_base_url.rstrip("/") if uflow_base_url else self.base_url
        self.timeout = timeout
        self.legacy_proxy_mode = legacy_proxy_mode
        self.endpoint_type = endpoint_type.lower()
        if self.endpoint_type not in ["admin", "enduser"]:
            raise ValueError("endpoint_type must be 'admin' or 'enduser'")
        self.token: Optional[str] = token  # Can be set during init or via login()
        self._claims_cache: Optional[Dict[str, Any]] = None

    def _get_path(self, endpoint: str, use_admin: bool = False) -> str:
        """
        Resolve path based on mode and endpoint type.
        
        Args:
            endpoint: Base endpoint path
            use_admin: Override to use admin endpoint (default: uses self.endpoint_type)
        
        Returns:
            Resolved endpoint path
        """
        if self.legacy_proxy_mode:
            # /legacy-api/* → /authmgr/*
            return f"/authmgr{endpoint}"
        else:
            # Standard endpoint routing
            # /uflow/ prefixed routes go to uflow_base_url
            if endpoint.startswith("/uflow/"):
                return endpoint
            
            # Determine prefix based on endpoint_type or override
            current_endpoint_type = "admin" if use_admin else self.endpoint_type
            prefix = "/auth/admin" if current_endpoint_type == "admin" else "/auth/user"
            
            # Map specific endpoints
            if endpoint == "/auth/user/verifyToken":
                return f"{prefix}/verifyToken"
            if endpoint == "/auth/user/generateToken":
                return f"{prefix}/generateToken"
            if endpoint == "/auth/user/permissions/check":
                return f"{prefix}/permissions/check"
            
            # Fallback for other /auth/user/ or /auth/admin/ endpoints
            if endpoint.startswith("/auth/user/"):
                return endpoint.replace("/auth/user/", f"{prefix}/")
            if endpoint.startswith("/auth/admin/"):
                return endpoint.replace("/auth/admin/", f"{prefix}/")
            
            return endpoint

    # ---------------------------
    # Token lifecycle (server calls)
    # ---------------------------

    def register(
        self,
        *,
        email: str,
        name: str,
        password: str,
        tenant_domain: str,
        uflow_base_url: Optional[str] = None
    ) -> dict:
        """
        Register a new admin user and tenant.
        
        Args:
            email: User email address
            name: User's full name
            password: User password (minimum 6 characters)
            tenant_domain: Unique tenant domain identifier
            uflow_base_url: User-flow base URL (optional, uses self.uflow_base_url if not provided)
        
        Returns:
            Registration response containing OTP and registration details
            
        Raises:
            HTTPError: If registration fails
            
        Example:
            >>> client = AuthSecClient("http://localhost:7468")
            >>> response = client.register(
            ...     email="admin@example.com",
            ...     name="Admin User",
            ...     password="SecurePass123!",
            ...     tenant_domain="example-tenant"
            ... )
            >>> print(response['otp'])  # OTP for dev/testing
        """
        base = uflow_base_url or self.uflow_base_url
        url = f"{base}/auth/admin/register"
        payload = {
            "email": email,
            "name": name,
            "password": password,
            "tenant_domain": tenant_domain
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def verify_registration(
        self,
        *,
        email: str,
        otp: str,
        uflow_base_url: Optional[str] = None
    ) -> dict:
        """
        Verify registration with OTP.
        
        Args:
            email: User email address
            otp: OTP code received during registration
            uflow_base_url: User-flow base URL (optional, uses self.uflow_base_url if not provided)
        
        Returns:
            Verification response containing tenant_domain, client_id, etc.
            
        Raises:
            HTTPError: If verification fails
        """
        base = uflow_base_url or self.uflow_base_url
        url = f"{base}/auth/admin/register/verify"
        payload = {
            "email": email,
            "otp": otp
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        
        # Handle empty response
        if not r.text:
            return {"verified": True}
        return r.json()

    def register_enduser(
        self,
        *,
        client_id: str,
        email: str,
        password: str,
        uflow_base_url: Optional[str] = None
    ) -> dict:
        """
        Register a new end-user within an existing client/tenant.
        
        This initiates end-user registration and sends an OTP for verification.
        Use this when registering users within an existing tenant (not creating new tenants).
        
        Args:
            client_id: Existing client UUID (tenant must already exist)
            email: User email address
            password: User password (minimum 6 characters)
            uflow_base_url: User-flow base URL (optional, uses self.uflow_base_url if not provided)
        
        Returns:
            Registration initiation response: {"email": str, "message": str}
            OTP is sent via email in production, may be included in response for dev/test environments
            
        Raises:
            HTTPError: If registration fails
            
        Example:
            >>> client = AuthSecClient("https://api.example.com", endpoint_type="enduser")
            >>> response = client.register_enduser(
            ...     client_id="existing-client-uuid",
            ...     email="user@example.com",
            ...     password="SecurePass123!"
            ... )
            >>> print(response['message'])  # "Registration initiated. Check email for OTP."
        """
        base = uflow_base_url or self.uflow_base_url
        url = f"{base}/auth/enduser/initiate-registration"
        payload = {
            "client_id": client_id,
            "email": email,
            "password": password
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def verify_enduser_registration(
        self,
        *,
        email: str,
        otp: str,
        uflow_base_url: Optional[str] = None
    ) -> dict:
        """
        Verify end-user registration with OTP.
        
        Completes the end-user registration process by verifying the OTP.
        Returns full account details including tenant_domain needed for login.
        
        Args:
            email: User email address
            otp: OTP code received via email (or in dev response)
            uflow_base_url: User-flow base URL (optional, uses self.uflow_base_url if not provided)
        
        Returns:
            Verification response with account details:
            {
                "client_id": str,
                "email_id": str,
                "project_id": str,
                "tenant_domain": str,
                "tenant_id": str
            }
            
        Raises:
            HTTPError: If verification fails
            
        Example:
            >>> response = client.verify_enduser_registration(
            ...     email="user@example.com",
            ...     otp="123456"
            ... )
            >>> tenant_domain = response['tenant_domain']
            >>> client_id = response['client_id']
        """
        base = uflow_base_url or self.uflow_base_url
        url = f"{base}/auth/enduser/verify-otp"
        payload = {
            "email": email,
            "otp": otp
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    # login() method removed - OTP/MFA required for authentication
    # Users should obtain tokens via web interface and use token parameter in __init__
    # See: https://app.authsec.dev for token generation
    
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
