# from jose import jwt, JWTError
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from typing import List

# # Secret key – in production load from ENV
# SECRET_KEY = "agent-secret-key"
# ALGORITHM = "HS256"

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Dummy user store (replace with DB)
# fake_users = {
#     "admin": {
#         "username": "admin",
#         "password": "admin123"  # hash in production!
#     }
# }

# def verify_token(required_groups: List[str] = None):
#     def _verify(token: str = Depends(oauth2_scheme)):
#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         except JWTError:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )

#         # Check group membership
#         if required_groups:
#             user_groups = payload.get("groups", [])
#             if not any(group in user_groups for group in required_groups):
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail=f"Missing required group. Need one of {required_groups}",
#                 )

#         return payload
#     return _verify
