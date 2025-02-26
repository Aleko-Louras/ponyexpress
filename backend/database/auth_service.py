import bcrypt
from datetime import datetime, timezone
from jose import jwt, ExpiredSignatureError, JWTError
import os
from backend.exceptions import InvalidAccessToken, ExpiredAccessToken

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-dev-key")
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "http://127.0.0.1"
JWT_DURATION = 3600

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt.

        Args:
            password (str): The plain-text password to be hashed.

        Returns:
            str: The hashed password as a string.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a password against its hashed version.

        Args:
            password (str): The plain-text password to verify.
            hashed_password (str): The hashed password stored in the database.

        Returns:
            bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def generate_claims(user_id: int) -> dict:
    """Generates JWT claims for an access token.

        Args:
            user_id (int): The ID of the user for whom the token is being generated.

        Returns:
            dict: A dictionary containing the JWT claims.
                - sub (str): Subject (user ID as a string).
                - iss (str): Issuer of the token.
                - iat (int): Issued-at timestamp.
                - exp (int): Expiry timestamp (1 hour after issue time).
    """
    iat = int(datetime.now(timezone.utc).timestamp())
    exp = iat + JWT_DURATION
    return {
        "sub": str(user_id),
        "iss": JWT_ISSUER,
        "iat": iat,
        "exp": exp
    }

def create_access_token(user_id: int) -> str:
    """Creates a JWT access token for a user.

        Args:
            user_id (int): The ID of the user to generate a token for.

        Returns:
            str: The encoded JWT access token.
    """
    claims = generate_claims(user_id)
    return jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decodes and verifies a JWT access token.

        Args:
            token (str): The JWT access token to decode.

        Returns:
            dict: The decoded payload of the JWT.

        Raises:
            ExpiredAccessToken: If the token has expired.
            InvalidAccessToken: If the token is invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], issuer=JWT_ISSUER)
        return payload
    except ExpiredSignatureError:
        raise ExpiredAccessToken()
    except JWTError:
        raise InvalidAccessToken()
