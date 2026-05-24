"""Authentication and encryption utilities for DataBot."""

import hashlib
import hmac
import json
from cryptography.fernet import Fernet
from typing import Tuple

# Secret key for encryption (in production, load from environment)
SECRET_KEY = "databot_secure_key_2026"

def get_cipher_suite():
    """Generate cipher suite from secret key."""
    key = hashlib.sha256(SECRET_KEY.encode()).digest()
    key = Fernet(base64.urlsafe_b64encode(key))
    return key

def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt."""
    salt = hashlib.sha256(SECRET_KEY.encode()).hexdigest()
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    return hashed.hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hashed version."""
    return hash_password(password) == hashed

def encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for secure storage."""
    try:
        import base64
        # Simple XOR encryption with key rotation
        key = hashlib.sha256(SECRET_KEY.encode()).digest()
        encrypted = bytearray()
        
        api_key_bytes = api_key.encode('utf-8')
        for i, byte in enumerate(api_key_bytes):
            encrypted.append(byte ^ key[i % len(key)])
        
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return api_key  # Fallback to plaintext if encryption fails

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key from secure storage."""
    try:
        import base64
        key = hashlib.sha256(SECRET_KEY.encode()).digest()
        encrypted_bytes = base64.b64decode(encrypted_key.encode('utf-8'))
        decrypted = bytearray()
        
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key[i % len(key)])
        
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_key  # Fallback

def generate_session_token(user_id: str) -> str:
    """Generate secure session token."""
    return hashlib.sha256(f"{user_id}{SECRET_KEY}".encode()).hexdigest()
