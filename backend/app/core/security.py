import jwt
import hashlib
import os
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from backend.app.core.config import settings

def hash_password(password: str) -> str:
    """Hashes password with salt using SHA-256."""
    salt = "di_salt_2026_"
    return hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None

def calculate_shannon_entropy(data: str) -> float:
    """Calculates Shannon entropy of a given string to detect high-entropy secrets."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy

def redact_secrets_text(text: str) -> str:
    """Redacts known API keys, tokens, and database credentials from code/logs."""
    patterns = [
        (r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]'),
        (r'ghp_[0-9a-zA-Z]{36}', '[REDACTED_GITHUB_TOKEN]'),
        (r'sk-[a-zA-Z0-9]{32,}', '[REDACTED_OPENAI_KEY]'),
        (r'(?i)(password|secret|passwd|token)\s*=\s*[\'"][^\'"]+[\'"]', r'\1="[REDACTED_SECRET]"'),
        (r'(?i)(postgres|mysql)://[^:]+:[^@]+@', r'\1://user:[REDACTED]@')
    ]
    redacted = text
    for pattern, repl in patterns:
        redacted = re.sub(pattern, repl, redacted)
    return redacted
