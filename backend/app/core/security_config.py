import os
from pydantic_settings import BaseSettings

class SecuritySettings(BaseSettings):
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short expiration
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Bcrypt Configuration
    BCRYPT_ROUNDS: int = 12
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT: str = "100/hour"
    AUTH_RATE_LIMIT: str = "5/minute"
    
    # Payload Limits
    MAX_CONTENT_LENGTH: int = 1 * 1024 * 1024  # 1MB
    
    # AES-256 Encryption Key (Must be 32 bytes for AES-256)
    # In production, this should be loaded from a secure vault
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "32-byte-long-secret-key-for-aes-256!!")
    
    # Security Headers
    SECURITY_HEADERS: dict = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # Allowed Origins for CORS
    ALLOWED_ORIGINS: list = ["http://localhost", "http://127.0.0.1"]
    
    # Audit Log Path
    AUDIT_LOG_PATH: str = "/app/data/audit.log"
    
    # Login Protection
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30

security_settings = SecuritySettings()
