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