from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from datetime import datetime, UTC
from app.models.user import User
from app.security.password import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)
from app.schemas.user import UserCreate, UserUpdate, UserChangePassword, UserLogin
from app.schemas.refresh_token import (
    RefreshTokenCreate,
    RefreshTokenResponse,
    RefreshTokenUpdate,
)
from app.core.logger_config import logger
from app.models.refresh_token import RefreshToken


class RefreshTokenCRUD:

    @staticmethod
    async def get_by_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
        try:
            result = await db.execute(
                select(RefreshToken).where(RefreshToken.token == token)
            )

            token_res = result.scalar_one_or_none()

            if not token_res:
                logger.debug(f"Токен: {token} не найден")

            return token_res

        except Exception as e:
            logger.error(f"Токен: {token} не найден : {e}")
            raise

    @staticmethod
    async def get_token_by_id(
        db: AsyncSession, token_id: int
    ) -> Optional[RefreshToken]:
        try:
            result = await db.execute(
                select(RefreshToken).where(RefreshToken.id == token_id)
            )

            res_token_id = result.scalar_one_or_none()

            if not res_token_id:
                logger.debug(f"Токен с ID: {token_id} не найден")
                return None
            return res_token_id

        except Exception as e:
            logger.error(f"Произошла ошибка получения токена с ID: {token_id}")
            raise

    @staticmethod
    async def create_token(
        db: AsyncSession, token_data: RefreshTokenCreate
    ) -> RefreshToken:
        try:

            existing_token = await RefreshTokenCRUD.get_by_token(db, token_data.token)

            if existing_token:
                raise ValueError(f"Такой рефреш токен уже существует")

            db_token = RefreshToken(
                user_id=token_data.user_id,
                token=token_data.token,
                expires_at=token_data.expires_at,
                is_revoked=False,
            )

            db.add(db_token)
            await db.commit()
            await db.refresh(db_token)
            logger.info(f"Создан refresh token для пользователя: {token_data.user_id}")
            return db_token

        except Exception as e:
            logger.error(f"Произошла ошибка создания токена:{e}")
            await db.rollback()
            raise

    @staticmethod
    async def revoke_token(db: AsyncSession, token: str) -> bool:
        try:
            db_token = await RefreshTokenCRUD.get_by_token(db, token)

            if not db_token:
                logger.warning(f"Попытка отозвать не существующий токен: {token}")
                return False

            if db_token.is_revoked:
                logger.debug(f"Токен: {token} уже отозван")
                return True

            db_token.is_revoked = True
            await db.commit()
            logger.info(f"Токен {token} отзван")
            return True
        except Exception as e:
            logger.error(f"Произошла ошибка отзывания токена:{token}:{e}")
            await db.rollback()
            raise

    @staticmethod
    async def valid_token(db: AsyncSession, token: str) -> bool:
        try:
            db_token = await RefreshTokenCRUD.get_by_token(db, token)

            if not db_token:
                logger.debug(f"Токен {token} не найден")
                return False

            is_valid = not db_token.is_revoked and db_token.expires_at > datetime.now(
                tz=UTC
            )

            if not is_valid:
                logger.debug(f"Токен: {token} не валидный")

            return is_valid

        except Exception as e:
            logger.error(f"Произошла ошибка проверки токена:{token} на валидность:{e}")
            return False

    @staticmethod
    async def revoke_all_users_tokens(db: AsyncSession, user_id: int) -> bool:
        # Отозвать все токены пользователя
        try:

            result = await db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user_id, RefreshToken.is_revoked == False
                )
            )

            tokens = result.scalars().all()

            if not tokens:
                logger.debug(f"Активных токенов у пользователя с ID: {user_id} нет")
                return True

            for token in tokens:
                token.is_revoked = True

            await db.commit()

            logger.info(f"Все токены пользователя с ID: {user_id} успешно отозваны")
            return True

        except Exception as e:
            logger.error(
                f"Произошла ошибка отзывания токенов пользователя с ID: {user_id}: {e}"
            )
            await db.rollback()
            raise

    @staticmethod
    async def delete_expired_tokens(db: AsyncSession) -> int:
        # Удалить все просроченые токены
        try:
            result = await db.execute(
                select(RefreshToken).where(
                    RefreshToken.expires_at <= datetime.now(tz=UTC)
                )
            )

            expired_tokens = result.scalars().all()

            if not expired_tokens:
                logger.debug(f"Очистка не требуется, истекших токенов нет")
                return 0

            for token in expired_tokens:
                await db.delete(token)

            await db.commit()

            logger.info(f"Удалено просроченных токенов: {len(expired_tokens)} шт")

            return len(expired_tokens)

        except Exception as e:
            logger.error(f"Ошибка очистки истекших токенов: {e}")
            await db.rollback()
            raise
