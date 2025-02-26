import bcrypt
from datetime import datetime, timezone
from jose import jwt, ExpiredSignatureError, JWTError
import os

from backend.exceptions import InvalidAccessToken, ExpiredAccessToken

# Environment Variables
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-dev-key")
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "http://127.0.0.1"
JWT_DURATION = 3600  # 1 hour

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def generate_claims(user_id: int) -> dict:
        iat = int(datetime.now(timezone.utc).timestamp())
        exp = iat + JWT_DURATION
        return {
            "sub": str(user_id),
            "iss": JWT_ISSUER,
            "iat": iat,
            "exp": exp
        }

    @staticmethod
    def create_access_token(user_id: int) -> str:
        claims = AuthService.generate_claims(user_id)
        return jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], issuer=JWT_ISSUER)
            return payload
        except ExpiredSignatureError:
            raise ExpiredAccessToken()
        except JWTError:
            raise InvalidAccessToken()
