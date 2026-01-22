# Changelog

All notable changes to the AuthSec Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-22

### Added
- Initial release of AuthSec Python SDK
- `AuthSecClient` for authentication and authorization
- `AdminHelper` for RBAC management
- Complete role CRUD operations (create, read, update, delete)
- Role binding management (create, list, remove)
- Permission management
- Scope management
- Support for both admin and end-user endpoints
- Environment variable configuration via `from_env()`
- Comprehensive error handling
- Type hints for better IDE support

### Features
- JWT token management
- User login/register
- OIDC token exchange
- Permission checking (simple and scoped)
- Multi-tenant support
- Audit logging support on backend
- Flexible endpoint configuration

### Documentation
- Complete README with examples
- API reference documentation
- Usage examples for common scenarios

[1.0.0]: https://github.com/authsec-ai/authsec-python-sdk/releases/tag/v1.0.0
