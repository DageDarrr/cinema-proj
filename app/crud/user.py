from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.security.password import verify_password
from app.models.user import User
from app.security.password import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)
from app.schemas.user import UserCreate, UserUpdate, UserChangePassword, UserLogin
from app.core.logger_config import logger


class UserCRUD:

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                logger.debug(f"Пользователь с ID: {user_id} не найден")

            return user

        except Exception as e:
            logger.error(f"Произошла при получении пользователя с ID:{user_id}:{e}")
            raise

    @staticmethod
    async def get_by_email(db: AsyncSession, user_email: str) -> Optional[User]:
        try:
            result = await db.execute(select(User).filter(User.email == user_email))

            user = result.scalar_one_or_none()

            if not user:
                logger.debug(f"Пользователь с email: {user_email} не найден")

            return user

        except Exception as e:
            logger.error(
                f"Произошла при получении пользователя с email:{user_email}:{e}"
            )
            raise

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        try:
            result = await db.execute(select(User).filter(User.username == username))

            user = result.scalar_one_or_none()

            if not user:
                logger.debug(f"Пользователь с username: {username} не найден")

            return user

        except Exception as e:
            logger.error(f"Произошла при получении пользователя с email:{username}:{e}")
            raise

    @staticmethod
    async def user_create(db: AsyncSession, user_data: UserCreate) -> User:
        try:
            existing_email = await UserCRUD.get_by_email(db, user_data.email)

            if existing_email:

                logger.warning(
                    f"Создание пользователя не удалось: email {user_data.email} уже существует"
                )
                raise ValueError("Пользователь с такой почтой уже существует")

            existing_username = await UserCRUD.get_by_username(db, user_data.username)

            if existing_username:
                logger.warning(
                    f"Создание пользователя не удалось: username {user_data.username} уже существует"
                )
                raise ValueError("Пользователь с таким username уже существует")

            hashed_password = get_password_hash(user_data.password)

            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
            )

            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

            logger.info(f"Пользователь: {user_data.username} успешно создан")

            return db_user

        except Exception as e:
            logger.error(f"Произошла ошибка создания пользователя: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def authenticate(db: AsyncSession, user_login: UserLogin) -> Optional[User]:
        try:
            db_user = await UserCRUD.get_by_username(db, user_login.username)
            if not db_user:
                logger.warning(
                    f"Не удачный вход пользователь с username: {user_login.username} не найден"
                )

                return None

            if not verify_password(user_login.password, db_user.hashed_password):
                logger.warning(
                    f"Не удачный вход: неверный пароль для пользователя: {user_login.username}"
                )
                return None

            logger.info(f"Успешный вход: пользователь:{user_login.username}")
            return db_user

        except Exception as e:
            logger.error(f"Произошла ошибка аутентификации пользователя: {e}")
            return None

    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        try:
            db_user = await UserCRUD.get_by_id(db, user_id)

            if not db_user:
                logger.warning(
                    f"Обновление не удалось: Пользователь с ID: {user_id} не найден"
                )
                return None

            if user_data.email and user_data.email != db_user.email:
                existing_email = await UserCRUD.get_by_email(db, user_data.email)
                if existing_email:
                    logger.warning(
                        f"Обновление не удалось email {user_data.email} уже существует"
                    )
                    raise ValueError("Пользователь с такой почтой уже существует")

            if user_data.username and user_data.username != db_user.username:
                existing_username = await UserCRUD.get_by_username(
                    db, username=user_data.username
                )

                if existing_username:
                    logger.warning(
                        f"Обновление не удалось пользователь с username: {user_data.username} уже существует"
                    )
                    raise ValueError("Пользователь с таким username уже существует")

            update_data = user_data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(db_user, field, value)

            await db.commit()
            await db.refresh(db_user)

            logger.info(f"Пользователь с ID: {user_id} успешно обновлен")
            return db_user

        except ValueError as e:
            logger.warning(
                f"Произошла ошибка валидации при обновлении пользователя: {e}"
            )
            raise

        except Exception as e:
            logger.error(
                f"Произошла ошибка обновления пользователя с ID:{user_id} : {e}"
            )
            await db.rollback()
            raise

    @staticmethod
    async def change_password(
        db: AsyncSession, user_id: int, password_change: UserChangePassword
    ) -> Optional[User]:
        try:
            db_user = await UserCRUD.get_by_id(db, user_id)
            if not db_user:
                logger.warning(
                    f"Смена пароля не удалась: пользователь {user_id} не найден"
                )
                return None

            if not verify_password(
                password_change.current_password, db_user.hashed_password
            ):
                logger.warning(
                    f"Смена пароля не удалась: неверный текущий пароль для пользователя {user_id}"
                )
                raise ValueError("Неверный текущий пароль")
            
            if verify_password(
                password_change.new_password, db_user.hashed_password
            ):
                raise ValueError("Новый пароль не должен совпадать со старым")
            

            validate_password_strength(password_change.new_password)
            hashed_password = get_password_hash(password_change.new_password)

            db_user.hashed_password = hashed_password
            await db.commit()
            await db.refresh(db_user)

            password_change.current_password = None
            password_change.new_password = None

            logger.info(f"Пароль успешно изменён для пользователя: {user_id}")
            return db_user

        except ValueError as e:
            logger.warning(
                f"Ошибка валидации при смене пароля для пользователя {user_id}: {e}"
            )
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Ошибка при смене пароля для пользователя {user_id}: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        try:
            db_user = await UserCRUD.get_by_id(db, user_id)
            if not db_user:
                logger.warning(f"Удаление не удалось: пользователь {user_id} не найден")
                return False

            await db.delete(db_user)
            await db.commit()

            logger.info(f"Пользователь успешно удалён: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
            await db.rollback()
            raise
