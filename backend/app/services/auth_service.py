from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import structlog
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.settings import settings
from app.database.db import Database
from app.repos.user_repository import User, UserRepository
from app.schemas.user_auth_schemas import Token, UserResponse

logger = structlog.get_logger(__name__)


class AuthService:
    def __init__(self, database: Database):
        self.database = database
        self.secret_key = settings.secrete_key
        self.algorithm = settings.algorithm

    def authenticate_user(self, username: str, password: str) -> UserResponse:
        with self.database.get_session() as session:
            user_repo = UserRepository(session)
            user: User = user_repo.get_user_by_username(username)

            if not user:
                logger.warning(
                    "auth_user_not_found",
                    username=username,
                )
                raise HTTPException(
                    status_code=401,
                    detail="Incorrect username or password",
                )

            if not self.verify_password(password, user.hashed_password):
                logger.warning(
                    "auth_invalid_password",
                    username=username,
                )
                raise HTTPException(
                    status_code=401,
                    detail="Incorrect username or password",
                )

            logger.info(
                "auth_user_authenticated",
                username=username,
            )

        return UserResponse(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=True,
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode(),
                hashed_password.encode(),
            )
        except Exception as e:
            logger.exception(str(e))

    def get_password_hash(self, password: str) -> str:
        try:
            return bcrypt.hashpw(
                password.encode(),
                bcrypt.gensalt(12),
            ).decode()
        except Exception as e:
            logger.exception(str(e))

    def create_access_token(self, user: UserResponse) -> str:
        try:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.expiration_minutes or 15
            )

            payload = {
                "sub": user.username,
                # "user_id": None,
                # "role": None,
                "type": "access",
                "exp": expire,
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            logger.debug(
                "access_token_created",
                username=user.username,
                exp=expire.isoformat(),
            )

            return token

        except Exception:
            logger.exception(
                "access_token_creation_failed",
                username=user.username,
            )
            raise HTTPException(
                status_code=500,
                detail="Token creation failed",
            )

    def decode_token(
        self, token: str, token_type: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

            if token_type and payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            return payload

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def login(self, username: str, password: str) -> Token:
        logger.info(
            "login_attempt",
            username=username,
        )

        user = self.authenticate_user(username, password)

        access_token = self.create_access_token(user)

        logger.info(
            "login_success",
            username=user.username,
        )

        return Token(
            access_token=access_token,
            # refresh_token=refresh_token,
            token_type="bearer",
        )

    def require_role(self, user: UserResponse, allowed_roles: list[str]):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
