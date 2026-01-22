"""
Environment Configuration Example

This example demonstrates:
- Using environment variables for configuration
- Best practices for managing secrets
- Different deployment scenarios
"""

import os
from authsec import AuthSecClient, AdminHelper


def example_basic_env():
    """Basic environment variable configuration"""
    
    print("🔧 Example: Basic Environment Configuration")
    print("=" * 50)
    
    # Set environment variables (in production, use .env file or system env)
    os.environ["AUTH_BASE_URL"] = "https://dev.api.authsec.dev"
    os.environ["CLIENT_ID"] = "your-client-id"
    
    # Read from environment
    base_url = os.getenv("AUTH_BASE_URL")
    client_id = os.getenv("CLIENT_ID")
    
    print(f"Base URL: {base_url}")
    print(f"Client ID: {client_id}")
    
    # Initialize client
    client = AuthSecClient(base_url)
    print("✅ Client initialized from environment variables")


def example_admin_from_env():
    """AdminHelper from environment variables"""
    
    print("\n🔧 Example: AdminHelper from Environment")
    print("=" * 50)
    
    # Set environment variables
    os.environ["ADMIN_TOKEN"] = "your-admin-token"
    os.environ["ADMIN_BASE_URL"] = "https://dev.api.authsec.dev"
    os.environ["ENDPOINT_TYPE"] = "enduser"
    os.environ["ADMIN_TIMEOUT"] = "20"
    
    try:
        # Create AdminHelper from environment
        admin = AdminHelper.from_env(debug=True)
        print("✅ AdminHelper created from environment")
        print(f"  Endpoint type: {admin.endpoint_type}")
        print(f"  Timeout: {admin.timeout}s")
    except ValueError as e:
        print(f"❌ Error: {e}")


def example_dotenv():
    """Using python-dotenv for .env file support"""
    
    print("\n🔧 Example: Using .env File")
    print("=" * 50)
    
    # Install: pip install python-dotenv
    try:
        from dotenv import load_dotenv
        
        # Load .env file
        load_dotenv()
        
        print("✅ Loaded environment from .env file")
        
        # Now use environment variables as normal
        client = AuthSecClient(os.getenv("AUTH_BASE_URL"))
        print(f"  Base URL: {client.base_url}")
    except ImportError:
        print("⚠️  python-dotenv not installed")
        print("  Install with: pip install python-dotenv")


def example_production_config():
    """Production configuration with proper secret management"""
    
    print("\n🔧 Example: Production Configuration")
    print("=" * 50)
    
    # In production, get secrets from secure sources
    # Examples:
    # - AWS Secrets Manager
    # - Azure Key Vault
    # - HashiCorp Vault
    # - Environment variables from deployment platform
    
    # Example: AWS Secrets Manager (requires boto3)
    # import boto3
    # import json
    # 
    # def get_secret(secret_name):
    #     client = boto3.client('secretsmanager', region_name='us-east-1')
    #     response = client.get_secret_value(SecretId=secret_name)
    #     return json.loads(response['SecretString'])
    # 
    # secrets = get_secret('authsec-credentials')
    # admin = AdminHelper(
    #     token=secrets['admin_token'],
    #     base_url=secrets['base_url']
    # )
    
    print("Best practices:")
    print("  ✅ Store secrets in secure vault (not in code)")
    print("  ✅ Use environment-specific configurations")
    print("  ✅ Rotate tokens regularly")
    print("  ✅ Use least-privilege access")
    print("  ✅ Enable debug mode only in development")


def example_multi_environment():
    """Managing multiple environments (dev/staging/prod)"""
    
    print("\n🔧 Example: Multi-Environment Configuration")
    print("=" * 50)
    
    # Determine environment
    env = os.getenv("APP_ENV", "development")
    
    # Environment-specific configuration
    config = {
        "development": {
            "base_url": "https://dev.api.authsec.dev",
            "debug": True,
            "timeout": 30
        },
        "staging": {
            "base_url": "https://staging.api.authsec.dev",
            "debug": True,
            "timeout": 20
        },
        "production": {
            "base_url": "https://api.authsec.dev",
            "debug": False,
            "timeout": 10
        }
    }
    
    env_config = config.get(env, config["development"])
    
    print(f"Environment: {env}")
    print(f"  Base URL: {env_config['base_url']}")
    print(f"  Debug: {env_config['debug']}")
    print(f"  Timeout: {env_config['timeout']}s")
    
    # Initialize with environment-specific config
    client = AuthSecClient(
        base_url=env_config["base_url"],
        timeout=env_config["timeout"]
    )
    print("✅ Client configured for", env)


def create_sample_env_file():
    """Create a sample .env file"""
    
    print("\n📝 Creating sample .env file...")
    
    env_content = """# AuthSec SDK Configuration

# Authentication Client Settings
AUTH_BASE_URL=https://dev.api.authsec.dev
CLIENT_ID=your-client-id-here

# Admin Helper Settings
ADMIN_TOKEN=your-admin-token-here
ADMIN_BASE_URL=https://dev.api.authsec.dev
ENDPOINT_TYPE=enduser
ADMIN_TIMEOUT=10

# Application Environment
APP_ENV=development

# Optional: User Credentials (for testing only - never commit to git!)
TEST_EMAIL=test@example.com
TEST_PASSWORD=test-password

# Debug Settings
DEBUG=true
"""
    
    try:
        with open(".env.example", "w") as f:
            f.write(env_content)
        print("✅ Created .env.example file")
        print("  Copy to .env and update with your values")
        print("  ⚠️  Never commit .env to version control!")
    except Exception as e:
        print(f"❌ Failed to create file: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("AuthSec SDK - Environment Configuration Examples")
    print("=" * 50)
    
    example_basic_env()
    example_admin_from_env()
    example_dotenv()
    example_production_config()
    example_multi_environment()
    
    # Uncomment to create .env.example file:
    # create_sample_env_file()
