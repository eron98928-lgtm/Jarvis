from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from .security_config import security_settings

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=security_settings.BCRYPT_ROUNDS
)

# AES-256 Encryption Setup
def get_encryption_key():
    # Derive a 32-byte key from the configured secret
    salt = b'jarvis_salt_fixed' # In production, use a unique salt per user/item
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(security_settings.ENCRYPTION_KEY.encode()))
    return key

fernet = Fernet(get_encryption_key())

def encrypt_data(data: str) -> str:
    """Encrypts sensitive data using AES-256."""
    if not data:
        return data
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    """Decrypts data using AES-256."""
    if not token:
        return token
    try:
        return fernet.decrypt(token.encode()).decode()
    except Exception:
        return "[DECRYPTION_ERROR]"

# Password Utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT Utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, security_settings.SECRET_KEY, algorithm=security_settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, security_settings.SECRET_KEY, algorithm=security_settings.ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, security_settings.SECRET_KEY, algorithms=[security_settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# Input Sanitization
def sanitize_input(text: str) -> str:
    """Basic sanitization to prevent common injections."""
    if not isinstance(text, str):
        return text
    # Remove common dangerous characters/patterns
    forbidden = ["<script>", "</script>", "javascript:", "onclick", "onerror"]
    sanitized = text
    for item in forbidden:
        sanitized = sanitized.replace(item, "")
    return sanitized.strip()
