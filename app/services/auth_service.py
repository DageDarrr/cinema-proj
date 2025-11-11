from datetime import timedelta, datetime, UTC
from app.core.config import settings
from app.crud.user import UserCRUD
from app.crud.refresh_token import RefreshTokenCRUD
from app.schemas.refresh_token import RefreshTokenCreate
from app.security.jwt import JWTManager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.logger_config import logger
from app.schemas.user import UserLogin
from app.models.user import User
from app.schemas.user import UserCreate



class AuthService:
    def __init__(self):
        self.jwt_manager = JWTManager()
        self.access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)
        self.refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_MIN)


    async def login(
            self,
            db : AsyncSession,
            login_data : UserLogin,

    )-> Optional[dict]:
        
        try:
            user = await UserCRUD.authenticate(db, login_data)
            if not user:
                logger.warning(f'Неудачная попытка входа для пользователя {login_data.username}')
                return None
            
            access_token = self.jwt_manager.create_access_token(subject=str(user.id),
                                                                expires_delta=self.access_token_expire,)
            
            refresh_token = self.jwt_manager.create_refresh_token(subject=str(user.id),
                                                                  expires_delta=self.refresh_token_expire,)
            
            expires_at = datetime.now(UTC) + self.refresh_token_expire

            refresh_token_data = RefreshTokenCreate(user_id=user.id,
                                                          token=refresh_token,
                                                          expires_at=expires_at)
            
            db_refresh_token = await RefreshTokenCRUD.create_token(db=db, token_data=refresh_token_data)

            logger.info(f'Успешный вход для пользователя {user.username}')

            return {
                "access_token" : access_token,
                "refresh_token" : refresh_token,
                "token_type" : "bearer",
                "user_id" : user.id,
                "username" : user.username
            }
        except Exception as e:
            logger.error(f'Произошла ошибка аутентификации пользователя: {user.username}:{e}')
            raise

    async def refresh_tokens(self,
                             db : AsyncSession,
                             refresh_token : str,
                             ) -> Optional[dict]:
        
        # Обновление пары токенов

        try:
            payload = self.jwt_manager.verify_refresh_token(refresh_token)
            if not payload:
                logger.warning(f'Невалидный refresh token')
                return None
            
            if not await RefreshTokenCRUD.valid_token(db=db, token=refresh_token):
                logger.warning(f'Токен не найден или отозван')
                return None
            
            user_id = int(payload.get("sub"))

            user = await UserCRUD.get_by_id(db, user_id)
            if not user:
                logger.warning(f"Пользователь с ID {user_id} не найден")
                return None
            
            await RefreshTokenCRUD.revoke_token(db=db, token=refresh_token)

            new_access_token = self.jwt_manager.create_access_token(subject=str(user.id),
                                                                expires_delta=self.access_token_expire,)
            
            new_refresh_token = self.jwt_manager.create_refresh_token(subject=str(user.id),
                                                                  expires_delta=self.refresh_token_expire,)
                                                                  
            expires_at=datetime.now(UTC) + self.refresh_token_expire

            new_refresh_token_data = RefreshTokenCreate(user_id=user.id,
                                                          token=new_refresh_token,
                                                          expires_at=expires_at)
            
            await RefreshTokenCRUD.create_token(db=db, token_data=new_refresh_token_data)

            logger.info(f'Токены обновлены для пользователя {user.username}')

            return {
                "access_token" : new_access_token,
                "refresh_token" : new_refresh_token,
                "token_type" : "bearer"
            }
        except Exception as e:
            logger.error(f"Произошла ошибка обновления токенов:{e}")
            raise

    async def logout(self,
                     db : AsyncSession,
                     refresh_token : str = None,
                     user_id : int = None) -> bool:
        
        try:
            if refresh_token and not user_id:
                payload = self.jwt_manager.verify_refresh_token(refresh_token)
                if payload:
                    user_id = int(payload.get("sub"))

            if refresh_token:
                success = await RefreshTokenCRUD.revoke_token(db, token=refresh_token)
                if success:
                    logger.info(f'Пользователь вышел с устройства: {refresh_token}')
                    return success
                return False
            
            elif user_id:
                # Выход со всех устройств
                success = await RefreshTokenCRUD.revoke_all_users_tokens(db, user_id=user_id)
                
            

                if success:
                    logger.info(f'Все токены пользователя:{user_id} отозваны')
                    return success
                return False

            else:
                logger.error(f'Для выхода надо указать refresh_token или user_id')
                return False
        
        except Exception as e:
            logger.error(f'Произошла ошибка выхода:{e}')
            raise

    
    async def valid_access_token(self,
                                 db : AsyncSession,
                                 token : str,
                                 )-> Optional[User]:
        
        try:
            payload = self.jwt_manager.verify_access_token(token=token)

            if not payload:
                return None
            
            user_id = int(payload.get("sub"))
            user = await UserCRUD.get_by_id(db,user_id=user_id)

            return user
        
        except Exception as e:
            logger.error(f'Произошла ошибка валидации токена:{e}')
            return None
        

    async def register(
        self,
        db: AsyncSession,
        user_data: UserCreate  
    ) -> Optional[dict]:
        """
        Регистрация нового пользователя с автоматическим логином
        """
        try:
           
            user = await UserCRUD.user_create(db, user_data)
            if not user:
                return None
            
            
            login_data = UserLogin(
                username=user_data.username,
                password=user_data.password
            )
            
            return await self.login(db, login_data)
            
        except Exception as e:
            logger.error(f'Ошибка регистрации пользователя: {e}')
            raise


            


    
                






            
        

        
    


    



