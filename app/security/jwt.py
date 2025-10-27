from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError

from app.core.config import settings
from app.core.logger_config import get_logger


logger = get_logger(__name__)


class JWTManager:
    def __init__(self):

        self.secret_key = settings.SECRET_KEY
        self.algoritm = settings.JWT_ALGORITHM

    def create_access_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:

        if expires_delta:
            expire = datetime.now(tz=UTC) + expires_delta
        else:
            expire = datetime.now(tz=UTC) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MIN
            )

        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access",
            "iat": datetime.now(tz=UTC),
        }

        if payload:
            to_encode.update(payload)

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algoritm)
        return encoded_jwt

    def create_refresh_token(
        self,
        subject: str,
        expires_delta: Optional[timedelta] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        if expires_delta:
            expire = datetime.now(tz=UTC) + expires_delta
        else:
            expire = datetime.now(tz=UTC) + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MIN
            )

        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh",
            "iat": datetime.now(tz=UTC),
        }

        if payload:
            to_encode.update(payload)

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algoritm)

    def verify_token(self, token) -> Optional[Dict[str, Any]]:
        "Общая проверка токена возвращает payload если все ОК"

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algoritm])
            return payload
        except PyJWTError as e:
            logger.error(f"Не валидный токен: {e}")
            return None

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:

        try:
            payload = self.verify_token(token=token)
            if payload and payload.get("type") == "access":
                return payload
            return None

        except PyJWTError as e:
            logger.error(f"Не валидный access token: {e}")
            return None

    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:

        try:
            payload = self.verify_token(token=token)
            if payload and payload.get("type") == "refresh":
                return payload
            return None

        except PyJWTError as e:
            logger.error(f"Не валидный refresh token: {e}")
            return None

    def get_token_payload(
        self,
        token: str,
    ) -> Optional[Dict[str, Any]]:

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algoritm],
                options={"verify_signature": False},
            )

            return payload

        except PyJWTError as e:
            logger.error(f"Не удалось раскодировать токен: {e}")
            return None

    def is_token_expired(
        self,
        token: str,
    ) -> bool:

        payload = self.get_token_payload(token=token)

        if not payload:
            return True

        exp_timestamp = payload.get("exp")

        if not exp_timestamp:
            return True

        expire_date = datetime.fromtimestamp(exp_timestamp, tz=UTC)

        return datetime.now(tz=UTC) > expire_date


jwt_manager = JWTManager()
