# auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Secret key – in production load from ENV
SECRET_KEY = "agent-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dummy user store (replace with DB)
fake_users = {
    "admin": {
        "username": "admin",
        "password": "admin123"  # hash in production!
    }
}

# auth.py
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    # Example: add user groups
    # In real apps, fetch groups from DB/LDAP/AD
    if "groups" not in to_encode:
        to_encode["groups"] = ["agent_group"]  # default group

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
