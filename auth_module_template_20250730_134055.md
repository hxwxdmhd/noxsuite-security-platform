# Authentication Module - Auto-Generated Template

## JWT Utils (jwt_utils.py)
```python
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def create_token(self, payload: Dict, expires_hours: int = 24) -> str:
        payload["exp"] = datetime.utcnow() + timedelta(hours=expires_hours)
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.InvalidTokenError:
            return None
```

## Auth Service (auth_service.py)
```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_utils import JWTManager

security = HTTPBearer()
jwt_manager = JWTManager("your-secret-key")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = jwt_manager.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
```

## Implementation Steps:
1. Create auth/ directory structure
2. Implement JWT utilities
3. Add FastAPI authentication dependencies
4. Create user management endpoints
5. Add TestSprite tests for auth flows
