from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.jwt_utils import JWTManager

security = HTTPBearer()
jwt_manager = JWTManager("your-secret-key")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    payload = jwt_manager.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
